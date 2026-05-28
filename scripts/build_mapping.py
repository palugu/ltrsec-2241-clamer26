#!/usr/bin/env python3
"""Walk pandoc-converted markdown and map sequential image references
(image1, image2, ...) to the semantic HEIC names (s1-t1-s2-3-1.png, ...).

Strategy:
  * Track current (scenario, task, step) heading context as we scan the markdown.
  * For each image reference inside a step, increment a per-step counter and
    pull the matching HEIC PNG by sorting available PNGs for that step.
  * Tiny inline icons (deploy button etc.) under 250px wide are skipped so
    they keep referencing the pandoc-extracted file (saved as icons later).
  * Scenario-level images (network diagrams) use s{N}.png.
  * Task-level images (deployment dialogs without a Step subheading) use
    s{N}-t{T}.png.
  * Blockquoted Task markers (`> **Task N: ...**`) are recognised so scenarios
    that don't use ## headings for tasks still resolve.
  * If a Step is encountered before any Task in a scenario, the task is
    inferred as 1.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

RAW_MD = Path("/tmp/ltrsec-conversion/lab-guide-raw.md")
HEIC_DIR = Path("/home/palugu/LTRSEC-2241-2026/ltrsec-2241-clamer26/docs/assets/screens")
PANDOC_MEDIA = Path("/tmp/ltrsec-conversion/extracted-media/media")

# Inline UI icons (deploy button etc.) are well under 250px. Real screenshots
# from the doc are 500px+ even after Word compression.
ICON_MAX_WIDTH = 250

SCENARIO_RE = re.compile(r"^# Scenario\s+(\d+)\b", re.IGNORECASE)
# Match ## Task N, or > **Task N: ...**
TASK_HEADING_RE = re.compile(r"^##\s+\*?\*?Task\s+(\d+)\b", re.IGNORECASE)
TASK_INLINE_RE = re.compile(r"^>\s*\*\*Task\s+(\d+)[: ]", re.IGNORECASE)
STEP_RE = re.compile(r"^###\s+\*?\*?Step\s+(\d+)\b", re.IGNORECASE)
IMG_RE = re.compile(r"<img\s+src=\"\./extracted-media/media/(image\d+\.(?:png|jpeg|jpg|gif))\"")
# Pandoc preserves Word's per-image style attributes. We capture the width
# (in inches) so the converted markdown can keep the original sizing intent
# from the lab guide ("small images 6-12cm, larger ones 16-16.5cm").
IMG_WIDTH_RE = re.compile(
    r"<img\s+src=\"\./extracted-media/media/(image\d+\.(?:png|jpeg|jpg|gif))\""
    r"(?:[^>]*?)style=\"[^\"]*?width:(\d+\.?\d*)in",
    re.DOTALL,
)


def parse_heic_key(stem: str) -> tuple[int, int, int, tuple]:
    parts = stem.split("-")
    scen = task = step = -1
    rest: list[int] = []
    for p in parts:
        if p == "edited":
            rest.append(99999)
        elif p.startswith("s") and p[1:].isdigit():
            n = int(p[1:])
            if scen == -1:
                scen = n
            else:
                step = n
        elif p.startswith("t") and p[1:].isdigit():
            task = int(p[1:])
        elif p.isdigit():
            rest.append(int(p))
    return (scen, task, step, tuple(rest))


def bucket_heic_files() -> dict[tuple, list[str]]:
    """Group converted PNG filenames by (scenario, task, step).

    For scenario-level network diagrams (s{N}.png + s{N}-edited.png), prefer
    the -edited variant first since those are the up-to-date topology images.
    """
    buckets: dict[tuple, list[tuple]] = defaultdict(list)
    extras: list[str] = []
    for png in sorted(HEIC_DIR.glob("*.png")):
        stem = png.stem
        if stem.startswith("pre-configured"):
            extras.append(stem)
            continue
        scen, task, step, rest = parse_heic_key(stem)
        if scen < 0:
            extras.append(stem)
            continue
        key = (scen, task, step)
        # Encode sort key so '-edited' floats above the plain scenario diagram
        # at the same level. '-edited' was parsed as rest=(99999,), so flip it.
        sort_key = (0, rest) if 99999 in rest else (1, rest)
        buckets[key].append((sort_key, stem))
    sorted_buckets: dict[tuple, list[str]] = {}
    for key, vals in buckets.items():
        vals.sort()
        sorted_buckets[key] = [v[1] for v in vals]
    return sorted_buckets


# Explicit overrides for images that appear before the first scenario heading
# (the Accessing Devices / Pre-configured Objects section).
PRESCENARIO_OVERRIDES: dict[str, str] = {
    "image6.jpeg": "pre-configured-branch-protected-network",
    "image8.jpeg": "pre-configured-hub-ac",
    "image9.jpeg": "pre-configured-spokes-ac",
}


_size_cache: dict[str, tuple[int, int]] = {}


def img_size(filename: str) -> tuple[int, int]:
    if filename in _size_cache:
        return _size_cache[filename]
    p = PANDOC_MEDIA / filename
    with Image.open(p) as im:
        _size_cache[filename] = im.size
    return _size_cache[filename]


def is_icon(filename: str) -> bool:
    try:
        w, _ = img_size(filename)
    except Exception:
        return False
    return w < ICON_MAX_WIDTH


def collect_widths(text: str) -> dict[str, float]:
    """Map each pandoc image filename to its source width in inches.

    Pandoc emits multi-line `<img>` tags AND prefixes those continuation
    lines with `> ` (blockquote) when the image sits inside a Word
    "indented" paragraph. We strip the blockquote prefixes first so the
    regex sees a clean multi-line tag and the width attribute is found
    reliably.
    """
    # Drop leading `> ` (any indent) on each line so the multi-line <img>
    # tags become contiguous text. This is non-destructive to anything else
    # we care about for width extraction.
    cleaned = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    widths: dict[str, float] = {}
    for m in IMG_WIDTH_RE.finditer(cleaned):
        fname = m.group(1)
        width = float(m.group(2))
        widths.setdefault(fname, width)
    return widths


def main() -> int:
    text = RAW_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    buckets = bucket_heic_files()
    widths = collect_widths(text)

    scen = -1
    task = -1
    step = -1
    cursor: dict[tuple, int] = defaultdict(int)
    mapping: dict[str, str] = {}
    icons: set[str] = set()
    unmapped: list[tuple[str, tuple]] = []

    for line in lines:
        m_scen = SCENARIO_RE.match(line)
        if m_scen:
            scen = int(m_scen.group(1))
            task = -1
            step = -1
            continue
        m_task = TASK_HEADING_RE.match(line) or TASK_INLINE_RE.match(line)
        if m_task:
            task = int(m_task.group(1))
            step = -1
            continue
        m_step = STEP_RE.match(line)
        if m_step:
            step = int(m_step.group(1))
            if scen >= 0 and task < 0:
                # Step seen inside scenario with no Task yet -> infer Task 1.
                task = 1
            continue
        for img in IMG_RE.findall(line):
            if img in mapping or img in icons:
                # Reused inline icon or already-mapped image; keep behaviour.
                if img in icons:
                    icons.add(img)
                continue
            if is_icon(img):
                icons.add(img)
                continue
            if scen < 0:
                if img in PRESCENARIO_OVERRIDES:
                    mapping[img] = PRESCENARIO_OVERRIDES[img]
                else:
                    unmapped.append((img, (scen, task, step)))
                continue
            for key in [(scen, task, step), (scen, task, -1), (scen, -1, -1)]:
                pool = buckets.get(key, [])
                idx = cursor[key]
                if idx < len(pool):
                    mapping[img] = pool[idx]
                    cursor[key] = idx + 1
                    break
            else:
                unmapped.append((img, (scen, task, step)))

    Path("/tmp/ltrsec-conversion/img_mapping.json").write_text(
        json.dumps(
            {
                "mapping": mapping,
                "icons": sorted(icons),
                "unmapped": unmapped,
                "widths_in": widths,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Mapped: {len(mapping)}  Icons skipped: {len(icons)}  Unmapped: {len(unmapped)}")
    leftovers = []
    for key, pool in buckets.items():
        used = cursor.get(key, 0)
        if used != len(pool):
            leftovers.append((key, used, len(pool), pool[used:]))
    if leftovers:
        print("HEIC files in unused bucket slots (may indicate doc-only images):")
        for key, used, total, remaining in leftovers:
            print(f"  {key}: used {used}/{total}  remaining={remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
