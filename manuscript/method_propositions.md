# Partial Identification in Expert-Crowd Elimination Systems

## Setup

Consider a decision round with a finite active set (A={1,ldots,n}). Let
(J_igeq 0) denote the observed expert score of alternative (i), and define
the normalized expert share

\[
j_i = \frac{J_i}{\sum_{k\in A}J_k},
\qquad \sum_{i\in A}j_i=1.
\]

The latent public preference vector is (F=(F_1,ldots,F_n)^	op), restricted
to the probability simplex

\[
\Delta^{n-1}=\left\{F\in\mathbb{R}^{n}:F_i\geq 0\ \forall i,
\ \mathbf{1}^{\top}F=1\right\}.
\]

Under percentage aggregation, the combined score is (C_i=j_i+F_i). Public
preference is not observed directly. The empirical information consists only
of an elimination outcome, a multiple-elimination set, or a final placement
order. Consequently, the relevant estimand is the set of preference vectors
consistent with the observed outcome, rather than a single reconstructed vote
vector.

For a direct single elimination of (e), consistency requires

\[
C_e\leq C_i \quad \text{for every }i\in A\setminus\{e\},
\]

or, equivalently,

\[
F_e-F_i\leq j_i-j_e.
\]

For a conservatively encoded multiple elimination (E\subset A), the same
comparison is imposed for every (e\in E) and every non-withdrawn survivor
(i\in A\setminus(E\cup W)), where (W) denotes withdrawals. No ordering is
imposed within (E). A withdrawal is excluded because leaving the system does
not reveal a relative combined-score comparison. A no-elimination round adds
no outcome inequality. When a complete final order is observed, every worse
placement is constrained to have a weakly lower combined score than every
better placement.

## Proposition 1: Polyhedral identified set under percentage aggregation

**Proposition 1.** *Under percentage aggregation, the set of public preference
shares consistent with an observed elimination outcome is a convex polytope
(possibly empty if the observed scores and encoded outcome are internally
inconsistent).* 

**Proof.** Public preference shares belong to the simplex
(Delta^{n-1}), which is the intersection of the affine hyperplane
(mathbf{1}^{\top}F=1) and the (n) nonnegative half-spaces (F_i\geq 0).
It is closed, bounded, and convex. Each direct-elimination comparison can be
written as

\[
(e_e-e_i)^{\top}F\leq j_i-j_e,
\]

where (e_i) is the (i)-th coordinate vector. Thus every observed outcome
condition is an affine half-space in (F). Multiple eliminations and complete
placement orders contribute only finitely many additional inequalities of the
same form. The consistency set is therefore the intersection of the simplex
with finitely many closed half-spaces. This intersection is a bounded
polyhedron and hence a convex polytope whenever nonempty. If the intersection
is empty, the encoded outcome is infeasible under the maintained aggregation
rule. (square)

This result is operationally important. Feasibility is a linear-programming
problem, and sharp coordinate-wise lower and upper bounds for each (F_i) are
obtained by minimizing and maximizing that coordinate over the same polytope.
The argument does not require a probabilistic model for public preferences.

## Proposition 2: Elimination-only feedback yields partial identification

**Proposition 2.** *Elimination-only feedback generally leads to partial rather
than point identification of public preferences.*

**Proof sketch.** The simplex restriction leaves (n-1) free dimensions. A
single observed elimination supplies relative weak inequalities, not numerical
equalities for the public shares. These inequalities identify an ordering
region for combined scores, but they do not generally bind at equality. If a
feasible vector satisfies all outcome inequalities strictly and lies in the
relative interior of the simplex, then a sufficiently small perturbation in
any direction tangent to the simplex remains feasible. The same elimination
outcome is therefore compatible with a continuum of distinct preference
vectors.

Equivalently, the observed event usually contains less independent information
than the number of unknown preference shares. Point identification may occur
only in exceptional boundary configurations in which the simplex and outcome
constraints collapse to a singleton. It is not implied by an ordinary
elimination observation. The identified object is thus the feasible preference
region

\[
\mathcal{F}(J,Y)=\{F\in\Delta^{n-1}: A_YF\leq b_Y(J)\},
\]

and its coordinate projections, rather than a unique latent public preference
vector. (square)

The interval

\[
[\underline F_i,\overline F_i]
=\left[\min_{F\in\mathcal F}F_i,\max_{F\in\mathcal F}F_i\right]
\]

is a sharp feasible-support interval under the maintained constraints. Its
width (overline F_i-\underline F_i) measures identification uncertainty, not
sampling error. Coordinate-wise midpoints are descriptive summaries and need
not combine into a jointly feasible vector.

## Proposition 3: Judge-save intervention weakens identification

**Proposition 3.** *Judge-save intervention weakens preference identifiability
relative to direct elimination because the observed eliminated contestant only
needs to belong to the bottom-two set under the combined rule, rather than be
the unique or weakly lowest-ranked contestant.*

**Theoretical argument.** Under direct elimination, observing the exit of
(e) implies

\[
\mathcal D_e=\{F\in\Delta^{n-1}:C_e(F)\leq C_i(F)\ \forall i\neq e\}.
\]

Under a judge-save mechanism, the public-expert aggregation first determines a
bottom-two set, after which an expert intervention selects the eliminated
contestant. The observed exit therefore implies only that (e) was a member
of some admissible bottom-two set. Denote the corresponding consistency set by
(mathcal S_e). Every vector that makes (e) the lowest combined-score
contestant also places (e) in the bottom two, so

\[
\mathcal D_e\subseteq\mathcal S_e.
\]

Set inclusion immediately implies weakly wider coordinate projections:

\[
\min_{F\in\mathcal S_e}F_i\leq\min_{F\in\mathcal D_e}F_i,
\qquad
\max_{F\in\mathcal S_e}F_i\geq\max_{F\in\mathcal D_e}F_i.
\]

Thus judge intervention cannot increase the identifying content of the same
elimination observation under otherwise fixed expert scores and candidate set;
it generally enlarges the feasible region. The empirical implementation uses
the corresponding ordinal bottom-set inclusion directly and reports both the
weak judge-save set and its direct-elimination benchmark, without replacing
either object by fabricated cardinal inequalities.

## Proposition 4: Ordinal rather than cardinal identification under ranking aggregation

**Proposition 4.** *Under ranking aggregation, hidden public preferences are
identified only up to a feasible set of ordinal rankings, rather than as
cardinal public vote shares.*

**Proof.** Let \(v=(v_1,\ldots,v_n)\) denote any cardinal public-preference
vector, and let \(r(v)\) be the strict fan ranking it induces. Under ranking
aggregation, the public component enters the decision rule only through
\(r(v)\): the combined score for alternative \(i\) is the sum of its expert
rank and its fan rank. Therefore, for any two cardinal vectors \(v\) and
\(v'\) satisfying \(r(v)=r(v')\), the combined rank scores, admissible
bottom sets, and observable elimination implications are identical. The two
vectors are observationally equivalent under the maintained mechanism.

The data can consequently eliminate fan-rank permutations that conflict with
the observed outcome, but cannot distinguish cardinal vectors within the
preimage of any retained permutation. The identified object is the feasible
ordinal set

\[
\mathcal R(J,Y)=\{r\in\mathfrak S_n:\ r\text{ is consistent with }(J,Y)\},
\]

not a unique vector of public shares. \(\square\)

## Proposition 5: Weak expansion under judge-save intervention

**Proposition 5.** *Under judge-save intervention, the feasible public-ranking
set weakly expands relative to direct ranking elimination because the observed
eliminated contestant need only belong to the bottom-two combined set rather
than be the unique or tie-inclusive worst contestant.*

**Proof.** Fix the active set, expert ranks, tie policy, and observed eliminated
contestant \(e\). Let \(\mathcal R_D\) be the fan-rank permutations for which
\(e\) belongs to the tie-inclusive worst combined-score set under direct
elimination. Let \(\mathcal R_S\) be the permutations for which \(e\) belongs
to the tie-inclusive bottom-two set under judge save. Membership in the worst
set implies membership in the bottom-two set, so every element of
\(\mathcal R_D\) also belongs to \(\mathcal R_S\). Hence

\[
\mathcal R_D\subseteq\mathcal R_S,
\qquad
|\mathcal R_S|\geq |\mathcal R_D|.
\]

The same argument extends conservatively to \(k\) observed eliminations by
comparing bottom-\(k\) membership with bottom-\((k+1)\) membership. Thus the
judge-save intervention cannot reduce the feasible ordinal set under otherwise
fixed inputs, and ranking uncertainty can only weakly increase. \(\square\)

## Implications for rule-aware inference

The propositions distinguish three sources of information. Cardinal
percentage aggregation yields a directly computable polytope. Ordinal ranking
aggregation identifies feasible public rankings rather than cardinal vote
shares and therefore requires combinatorial enumeration or validated sampling.
Judge-save intervention further coarsens the outcome signal by inserting an
expert choice after bottom-two formation. A rule-aware analysis must preserve
these differences; treating all three mechanisms as the same cardinal model
would overstate preference identifiability. The implemented feasible-ranking
sets, normalized rank widths, and ranking entropies operationalize these
distinctions without claiming recovery of latent cardinal vote shares.
