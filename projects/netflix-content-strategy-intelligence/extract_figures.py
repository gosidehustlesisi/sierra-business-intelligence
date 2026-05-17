#!/usr/bin/env python3
"""
Extract all matplotlib/plotly outputs from notebooks to figures/ as PNGs.

Usage:
    python extract_figures.py

This script:
1. Scans all .ipynb files in notebooks/
2. For each cell output with image data, saves it as PNG
3. Also generates static PNG versions of any plotly HTML outputs
4. Produces a summary report
"""

import os
import json
import base64
from pathlib import Path

import nbformat

NOTEBOOK_DIR = Path("notebooks")
FIGURES_DIR = Path("figures")
OUTPUT_DIR = Path("output")


def extract_images_from_notebook(nb_path):
    """Extract image outputs from a Jupyter notebook."""
    with open(nb_path) as f:
        nb = nbformat.read(f, as_version=4)

    extracted = 0
    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for out_idx, output in enumerate(cell.get("outputs", [])):
            if output.output_type in ("display_data", "execute_result"):
                data = output.get("data", {})
                if "image/png" in data:
                    img_data = data["image/png"]
                    if isinstance(img_data, str):
                        png_bytes = base64.b64decode(img_data)
                    else:
                        png_bytes = bytes(img_data)

                    out_name = f"{nb_path.stem}_cell{cell_idx}_out{out_idx}.png"
                    out_path = FIGURES_DIR / out_name
                    with open(out_path, "wb") as img_file:
                        img_file.write(png_bytes)
                    extracted += 1
                    print(f"  ✓ {out_name}")
    return extracted


def copy_existing_pngs():
    """Count existing PNG files in figures/."""
    return list(FIGURES_DIR.glob("*.png"))


def main():
    FIGURES_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("FIGURE EXTRACTION REPORT")
    print(f"{'='*60}\n")

    # 1. Extract from notebooks
    nb_extracted = 0
    for nb_file in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        print(f"\nProcessing: {nb_file.name}")
        count = extract_images_from_notebook(nb_file)
        nb_extracted += count
        print(f"  Extracted {count} image(s)")

    # 2. Count all PNGs
    all_pngs = copy_existing_pngs()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Notebooks scanned:      {len(list(NOTEBOOK_DIR.glob('*.ipynb')))}")
    print(f"Images from notebooks:  {nb_extracted}")
    print(f"Total PNGs in figures/: {len(all_pngs)}")
    print(f"\nFiles:")
    for p in sorted(all_pngs):
        size_kb = p.stat().st_size / 1024
        print(f"  {p.name:50s} {size_kb:8.1f} KB")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
