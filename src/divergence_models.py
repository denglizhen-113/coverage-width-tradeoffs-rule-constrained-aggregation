"""Interpretable expert and latent-public channel models."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = ["age", "returning_numeric", "week", "n_active"]
CATEGORICAL_FEATURES = [
    "aggregation_regime",
    "season_category",
    "industry_group",
    "partner_group",
]


@dataclass(frozen=True)
class ChannelFit:
    coefficients: pd.DataFrame
    predictions: np.ndarray
    summary: dict[str, Any]


def prepare_divergence_data(features: pd.DataFrame) -> pd.DataFrame:
    required = {
        "judge_pct",
        "public_appeal_proxy",
        "public_appeal_uncertainty",
        "age",
        "returning_contestant",
        "week",
        "n_active",
        "aggregation_regime",
        "season",
        "contestant_season_id",
        "partner_clean",
        "industry_profession",
    }
    missing = sorted(required.difference(features.columns))
    if missing:
        raise ValueError(f"features are missing required columns: {missing}")
    data = features.loc[
        features["judge_pct"].notna() & features["public_appeal_proxy"].notna()
    ].copy()
    if data.empty:
        raise ValueError("No rows have both expert and public-channel outcomes.")
    data["returning_numeric"] = data["returning_contestant"].astype(str).str.casefold().isin(
        {"true", "1", "yes"}
    ).astype(float)
    data["season_category"] = data["season"].astype(int).astype(str)
    data["industry_group"] = data["industry_profession"].fillna("Missing").astype(str)
    partner = data["partner_clean"].fillna("Missing").astype(str)
    top_partners = set(partner.value_counts().head(20).index)
    data["partner_group"] = partner.where(partner.isin(top_partners), "Other")
    return data.reset_index(drop=True)


def winsorized_inverse_uncertainty(
    uncertainty: pd.Series, epsilon: float = 0.05, lower_q: float = 0.05, upper_q: float = 0.95
) -> tuple[np.ndarray, dict[str, float]]:
    values = pd.to_numeric(uncertainty, errors="coerce").to_numpy(dtype=float)
    fill = float(np.nanmedian(values)) if np.isfinite(values).any() else 1.0
    values = np.where(np.isfinite(values), np.clip(values, 0.0, 1.0), fill)
    raw = 1.0 / (values + epsilon)
    lower = float(np.quantile(raw, lower_q))
    upper = float(np.quantile(raw, upper_q))
    weights = np.clip(raw, lower, upper)
    weights /= weights.mean()
    return weights, {
        "epsilon": epsilon,
        "raw_min": float(raw.min()),
        "raw_max": float(raw.max()),
        "winsor_lower": lower,
        "winsor_upper": upper,
        "normalized_min": float(weights.min()),
        "normalized_max": float(weights.max()),
    }


def _preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore", drop="first", sparse_output=False
                ),
            ),
        ]
    )
    return ColumnTransformer(
        [("numeric", numeric, NUMERIC_FEATURES), ("categorical", categorical, CATEGORICAL_FEATURES)],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def fit_channel(
    data: pd.DataFrame,
    target: str,
    *,
    model_type: str,
    sample_weight: np.ndarray | None = None,
) -> ChannelFit:
    if target not in data:
        raise ValueError(f"Unknown target: {target}")
    y = pd.to_numeric(data[target], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(y).all() or np.std(y) <= 0:
        raise ValueError(f"Target {target} is missing or constant.")
    y_mean = float(np.mean(y))
    y_std = float(np.std(y, ddof=0))
    y_z = (y - y_mean) / y_std
    preprocessor = _preprocessor()
    if model_type == "ols":
        estimator: LinearRegression | RidgeCV = LinearRegression()
    elif model_type == "ridge_cv":
        estimator = RidgeCV(alphas=np.logspace(-4, 4, 25))
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    pipeline = Pipeline([("preprocess", preprocessor), ("model", estimator)])
    fit_kwargs = {"model__sample_weight": sample_weight} if sample_weight is not None else {}
    pipeline.fit(data, y_z, **fit_kwargs)
    predictions = pipeline.predict(data)
    fitted_preprocessor = pipeline.named_steps["preprocess"]
    fitted_model = pipeline.named_steps["model"]
    names = fitted_preprocessor.get_feature_names_out()
    coefficients = pd.DataFrame(
        {
            "variable": names,
            "coefficient": np.asarray(fitted_model.coef_, dtype=float),
            "target": target,
            "model_type": model_type,
            "weighted": sample_weight is not None,
        }
    )
    coefficients = pd.concat(
        [
            pd.DataFrame(
                {
                    "variable": ["intercept"],
                    "coefficient": [float(fitted_model.intercept_)],
                    "target": [target],
                    "model_type": [model_type],
                    "weighted": [sample_weight is not None],
                }
            ),
            coefficients,
        ],
        ignore_index=True,
    )
    summary = {
        "target": target,
        "model_type": model_type,
        "weighted": sample_weight is not None,
        "n_observations": len(data),
        "n_features": len(names),
        "target_mean": y_mean,
        "target_std": y_std,
        "r_squared": float(r2_score(y_z, predictions, sample_weight=sample_weight)),
        "selected_alpha": (
            float(fitted_model.alpha_) if isinstance(fitted_model, RidgeCV) else np.nan
        ),
    }
    return ChannelFit(coefficients, predictions, summary)


def try_mixedlm(data: pd.DataFrame, target: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Attempt season plus contestant random intercepts; return a logged fallback."""
    status: dict[str, Any] = {
        "target": target,
        "model_type": "mixedlm",
        "success": False,
        "converged": False,
        "message": "",
    }
    try:
        import statsmodels.formula.api as smf

        frame = data.copy()
        target_values = pd.to_numeric(frame[target], errors="coerce")
        frame["target_z"] = (target_values - target_values.mean()) / target_values.std(ddof=0)
        for column in ("age", "week", "n_active"):
            values = pd.to_numeric(frame[column], errors="coerce")
            frame[f"{column}_z"] = (values - values.mean()) / values.std(ddof=0)
        formula = (
            "target_z ~ age_z + returning_numeric + week_z + n_active_z "
            "+ C(aggregation_regime)"
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = smf.mixedlm(
                formula,
                frame,
                groups=frame["season"].astype(str),
                re_formula="1",
                vc_formula={"contestant": "0 + C(contestant_season_id)"},
            )
            fitted = model.fit(reml=False, method="lbfgs", maxiter=200, disp=False)
        warning_text = "; ".join(str(item.message) for item in caught)
        status.update(
            {
                "success": bool(fitted.converged),
                "converged": bool(fitted.converged),
                "message": warning_text or "converged",
                "log_likelihood": float(fitted.llf),
                "n_observations": int(fitted.nobs),
            }
        )
        if not fitted.converged:
            return pd.DataFrame(), status
        fixed = fitted.fe_params
        rows = pd.DataFrame(
            {
                "variable": fixed.index,
                "coefficient": fixed.to_numpy(dtype=float),
                "target": target,
                "model_type": "mixedlm",
                "weighted": False,
            }
        )
        return rows, status
    except Exception as exc:  # statsmodels exposes several optimizer exceptions
        status["message"] = f"{type(exc).__name__}: {exc}"
        return pd.DataFrame(), status


def build_divergence_table(
    expert_coefficients: pd.DataFrame, crowd_coefficients: pd.DataFrame
) -> pd.DataFrame:
    expert = expert_coefficients.loc[
        expert_coefficients["model_type"].eq("ridge_cv")
        & ~expert_coefficients["weighted"]
    ][["variable", "coefficient"]].rename(columns={"coefficient": "expert_coef"})
    crowd = crowd_coefficients.loc[
        crowd_coefficients["model_type"].eq("ridge_cv")
        & crowd_coefficients["weighted"]
    ][["variable", "coefficient"]].rename(columns={"coefficient": "crowd_coef"})
    merged = expert.merge(crowd, on="variable", how="inner", validate="1:1")
    merged["difference"] = merged["crowd_coef"] - merged["expert_coef"]
    merged["sign_divergence"] = (
        np.sign(merged["expert_coef"]) != np.sign(merged["crowd_coef"])
    ) & merged[["expert_coef", "crowd_coef"]].abs().gt(1e-8).all(axis=1)
    merged["relative_magnitude"] = np.where(
        merged["expert_coef"].abs() > 1e-8,
        merged["crowd_coef"].abs() / merged["expert_coef"].abs(),
        np.nan,
    )
    merged["model_type"] = "expert_ridge_vs_uncertainty_weighted_crowd_ridge"
    merged["notes"] = "Standardized descriptive coefficients; no causal interpretation."
    return merged.sort_values("difference", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
