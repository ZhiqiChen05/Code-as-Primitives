#!/usr/bin/env python3
"""Export the manuscript's original figures for the project website.

Run with PyMuPDF and Pillow installed:
    python3 scripts/prepare_paper_figures.py --source-dir ../ExtendedAbstract

The source directory is read only. The overview PNG is rasterized from its PDF;
the PDF, results PNG, and embedded Pen JPEGs are copied without image edits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import pymupdf
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "assets" / "figures"
IMAGES = ROOT / "assets" / "images"

# Original images embedded in Figure 1, ordered left-to-right in the low-level
# control row. Bounding boxes are recorded from the PDF, rather than inferred
# from a rendered page. No crop, upscaling, or recompression is applied.
PEN_FRAMES = (
    ("initial", 40, "The dexterous hand holds the pen in its initial orientation."),
    ("tilt", 42, "The dexterous hand tilts the pen during reorientation."),
    ("upright", 43, "The dexterous hand brings the pen upright."),
    ("target", 44, "The dexterous hand reaches the target pen orientation."),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_metadata(path: Path, **extra: object) -> dict[str, object]:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "path": str(path.relative_to(ROOT)),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        **extra,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT.parent / "ExtendedAbstract")
    parser.add_argument("--width", type=int, default=2400)
    args = parser.parse_args()
    if args.width <= 0:
        parser.error("--width must be positive")

    source = args.source_dir.resolve() / "figs"
    source_pdf = source / "fig1_pen_v3-1.pdf"
    source_results = source / "heldout_pair.png"
    if not source_pdf.is_file() or not source_results.is_file():
        parser.error("source directory must contain figs/fig1_pen_v3-1.pdf and figs/heldout_pair.png")

    FIGURES.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    overview_pdf = FIGURES / "paper-overview.pdf"
    overview_png = FIGURES / "paper-overview.png"
    results_png = FIGURES / "paper-heldout-pair.png"
    shutil.copyfile(source_pdf, overview_pdf)
    shutil.copyfile(source_results, results_png)

    with pymupdf.open(source_pdf) as document:
        if len(document) != 1:
            raise ValueError("The expected Figure 1 PDF must contain exactly one page")
        page = document[0]
        scale = args.width / page.rect.width
        page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).save(overview_png)

        frames = []
        for name, xref, alt in PEN_FRAMES:
            embedded = document.extract_image(xref)
            if embedded["ext"] != "jpeg":
                raise ValueError(f"Expected original JPEG at PDF image {xref}")
            path = IMAGES / f"paper-pen-{name}.jpg"
            path.write_bytes(embedded["image"])
            frames.append(image_metadata(
                path,
                stage=name,
                alt=alt,
                source="figs/fig1_pen_v3-1.pdf",
                pdf_page=1,
                pdf_image_xref=xref,
                pdf_image_bboxes_points=[list(rect) for rect in page.get_image_rects(xref)],
                processing="Original embedded JPEG extraction; no crop or recompression.",
            ))

        manifest = {
            "source": "ExtendedAbstract/main.tex and its original figure assets",
            "overview": image_metadata(
                overview_png,
                alt="Code as Primitives overview: a high-level plan invokes a pen-rotation skill; a dexterous hand reorients the pen; a frontier model designs a controller, searches candidate policies through rollouts, and freezes the accepted policy.",
                caption="Code as Primitives synthesizes the low-level skill itself. A frontier model designs a parameterized controller, searches its parameters with simulation rollouts, and freezes the resulting program for standalone execution.",
                source="figs/fig1_pen_v3-1.pdf",
                source_sha256=sha256(source_pdf),
                pdf_page=1,
                pdf_page_size_points=[page.rect.width, page.rect.height],
                original_pdf=str(overview_pdf.relative_to(ROOT)),
                original_pdf_bytes=overview_pdf.stat().st_size,
                note="The 30/30 held-out successes shown in this figure refer to the illustrated Pen example, not the DexVerse evaluation protocol.",
            ),
            "heldout_results": image_metadata(
                results_png,
                alt="Two radar charts of held-out DexVerse success. Left: agentic and CEM search versus the strongest imitation-learning baseline on 15 tasks. Right: agentic and CEM search across six categories covering the remaining 60 tasks, with lower success on long-horizon tasks.",
                caption="Held-out success on DexVerse. (a) Code as Primitives compared with the strongest result among pi0.5, OpenVLA, DP3, and DP on 15 tasks with published imitation-learning baselines. (b) Agentic and CEM search across the remaining 60 tasks.",
                source="figs/heldout_pair.png",
                source_sha256=sha256(source_results),
                processing="Byte-for-byte copy of the original paper figure.",
                note="Panel (b) is titled 'rest of DexVerse' and its category task counts sum to 60. The manuscript caption's 'full DexVerse benchmark' wording is broader than the panel's coverage.",
            ),
            "pen_frames": frames,
        }

    manifest_path = FIGURES / "paper-assets.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for item in [manifest["overview"], manifest["heldout_results"], *frames]:
        print(f"{item['path']}: {item['width']} x {item['height']}, {item['bytes']:,} bytes")
    print(f"{overview_pdf.relative_to(ROOT)}: {overview_pdf.stat().st_size:,} bytes")
    print(manifest_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
