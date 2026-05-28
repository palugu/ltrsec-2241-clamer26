#!/usr/bin/env python3
"""Convert HEIC files in Screens/ to PNG with the same base name.

Outputs to OUTPUT_DIR with kebab-case (lowercase, dots->dashes) filenames so that
they're URL-friendly for the mkdocs site.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

SOURCE_DIR = Path("/home/palugu/LTRSEC-2241-2026/Screens")
OUTPUT_DIR = Path("/home/palugu/LTRSEC-2241-2026/ltrsec-2241-clamer26/docs/assets/screens")

# Cap large screenshots to a sensible width to keep the site light. mkdocs-material
# / glightbox lets users zoom, so 1600px is plenty for retina screens.
MAX_WIDTH = 1600


def normalize_name(stem: str) -> str:
    """Turn 'S1.T1.S2.3' into 's1-t1-s2-3' which is URL/web friendly."""
    return stem.lower().replace(".", "-").replace("_", "-")


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"Source dir not found: {SOURCE_DIR}", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    heic_files = sorted(SOURCE_DIR.glob("*.heic")) + sorted(SOURCE_DIR.glob("*.HEIC"))
    if not heic_files:
        print("No HEIC files found", file=sys.stderr)
        return 1

    print(f"Found {len(heic_files)} HEIC files. Converting to PNG ...")
    converted = 0
    skipped = 0
    for src in heic_files:
        dest = OUTPUT_DIR / f"{normalize_name(src.stem)}.png"
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            skipped += 1
            continue
        try:
            with Image.open(src) as img:
                # Strip metadata (orientation already applied by Pillow on load),
                # convert to RGB to remove HEIC-specific channels.
                img = img.convert("RGB")
                if img.width > MAX_WIDTH:
                    new_h = round(img.height * MAX_WIDTH / img.width)
                    img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)
                img.save(dest, "PNG", optimize=True)
            converted += 1
            if converted % 25 == 0:
                print(f"  ... {converted} converted")
        except Exception as exc:
            print(f"FAILED: {src.name}: {exc}", file=sys.stderr)

    print(f"Done. converted={converted}, skipped={skipped}, total={len(heic_files)}")
    print(f"Output: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
