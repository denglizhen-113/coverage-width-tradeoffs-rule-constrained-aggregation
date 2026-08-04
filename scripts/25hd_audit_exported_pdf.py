"""Audit a locally exported Stage 25H-D PDF without modifying it."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader


REQUIRED_PREVIEW = Path(
    "submission_package_stage25/02_submission_files/"
    "DSS_anonymized_manuscript_STAGE25H_D_final_preview.pdf"
)
DSS_PAGE_LIMIT = 34
IDENTITY_MARKERS = (
    "Deng Lizhen",
    "Liu Yuxin",
    "Li Bo",
    "Huazhong University of Science and Technology",
    "Wuhan University of Technology",
    "3070116993@qq.com",
    "Corresponding Author",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a local WPS PDF export for Stage 25H-D eligibility."
    )
    parser.add_argument("--pdf", type=Path, required=True, help="PDF to audit.")
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Generated Markdown audit report.",
    )
    parser.add_argument(
        "--render-dir",
        type=Path,
        required=True,
        help="Directory for local, non-submission page PNGs.",
    )
    parser.add_argument(
        "--visual-review-pages",
        default="not recorded",
        help="Comma-separated rendered pages reviewed visually during this run.",
    )
    parser.add_argument(
        "--visual-findings",
        default="not recorded",
        help="Observed visual findings from the rendered pages.",
    )
    return parser.parse_args()


def render_pages(pdf_path: Path, render_dir: Path) -> int:
    render_dir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf_path))
    for page_index in range(len(document)):
        page = document[page_index]
        image = page.render(scale=1.7).to_pil()
        image.save(render_dir / f"page-{page_index + 1:02d}.png")
    return len(document)


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf.resolve()
    report_path = args.report.resolve()
    render_dir = args.render_dir.resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    page_text = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(page_text)
    identity_hits = [marker for marker in IDENTITY_MARKERS if marker.lower() in text.lower()]
    image_counts = [len(page.images) for page in reader.pages]
    total_image_objects = sum(image_counts)
    figure_caption_pages = [
        index + 1 for index, value in enumerate(page_text) if re.search(r"\bFigure\s+\d+\b", value)
    ]
    table_caption_pages = [
        index + 1 for index, value in enumerate(page_text) if re.search(r"\bTable\s+\d+\b", value)
    ]
    rendered_pages = render_pages(pdf_path, render_dir)
    required_preview = (Path.cwd() / REQUIRED_PREVIEW).resolve()
    is_required_preview = pdf_path == required_preview
    anonymous_safe = not identity_hits
    page_limit_ok = len(reader.pages) <= DSS_PAGE_LIMIT
    acceptable = is_required_preview and anonymous_safe and page_limit_ok and rendered_pages > 0
    metadata = dict(reader.metadata or {})

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(
            [
                "# Stage 25H-D Local PDF Export Audit",
                "",
                f"- Audited PDF: `{pdf_path}`",
                f"- Page count: {len(reader.pages)}",
                f"- DSS {DSS_PAGE_LIMIT}-page limit: {'pass' if page_limit_ok else 'fail'}",
                f"- Required H-D anonymized preview path: `{required_preview}`",
                f"- Required preview path matched: {'yes' if is_required_preview else 'no'}",
                f"- Page PNGs rendered for inspection: {rendered_pages}",
                f"- Pages visually reviewed: {args.visual_review_pages}",
                f"- Visual findings: {args.visual_findings}",
                f"- PDF producer/creator: {metadata.get('/Creator', '') or metadata.get('/Producer', '') or 'not stated'}",
                f"- Embedded raster-image objects by page: {image_counts}",
                f"- Total embedded raster-image objects: {total_image_objects}",
                f"- Figure-caption text found on pages: {figure_caption_pages or 'none'}",
                f"- Table-caption text found on pages: {table_caption_pages or 'none'}",
                f"- Author-identity markers found: {identity_hits or 'none'}",
                f"- Double-anonymization status: {'pass' if anonymous_safe else 'fail'}",
                "",
                "## Eligibility Decision",
                "",
                "ELIGIBLE_FOR_STAGE25H_D_PAGE_COUNT" if acceptable else "NOT_ELIGIBLE_FOR_STAGE25H_D_PAGE_COUNT",
                "",
                "This PDF must not supply the final Stage 25H-D page count unless it is the required anonymized "
                "preview file, passes the double-anonymization check, and satisfies the DSS page limit. Page PNGs "
                "are local QA artifacts only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"pages={len(reader.pages)}")
    print(f"anonymous_safe={anonymous_safe}")
    print(f"required_preview_path_matched={is_required_preview}")
    print(f"eligible_for_stage25h_d_page_count={acceptable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
