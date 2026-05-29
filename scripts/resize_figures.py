"""Normalize the ``max-width`` of every <figure> in the lab guide.

The conversion pipeline (``process_markdown.py``) seeds each figure with the
width recorded in the source DOCX. That works for the printable Word
document but produces an inconsistent visual rhythm when the same figure is
rendered in the MkDocs HTML/PDF: portrait dialog screenshots that the DOCX
sized at "page width" balloon up next to the slim landscape diagrams.

This script re-sizes every figure based on the *pixel* dimensions of the
underlying PNG so the rendered page has a predictable rhythm:

* Landscape (aspect >= 1.3) – capped at **16 cm** so every wide screenshot
  fills the same column.
* Square-ish (1.0 <= aspect < 1.3) – capped at **12 cm**.
* Portrait (aspect < 1.0) – target rendered height ≈ 11 cm, so the width is
  ``round(11 × aspect, 1)`` clamped to the range 6–12 cm.

Figures whose current ``max-width`` is already below 13 cm are treated as
intentional "deploy" / inline screenshots and left untouched.

The script is idempotent: running it twice produces no further changes.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
SCREENS = DOCS / "assets" / "screens"

# Matches the <figure markdown> blocks emitted by process_markdown.py. The
# regex is permissive about whitespace so it survives manual hand-editing.
FIGURE_BLOCK_RE = re.compile(
    r"<figure markdown\s+style=\"max-width:(?P<cm>[\d.]+)cm;\"[^>]*?>\s*"
    r"!\[(?P<alt>[^]]*)\]\(assets/screens/(?P<file>[^)\s]+)\)"
    r"(?P<attrs>[^\n]*)\n\s*</figure>",
    re.DOTALL,
)

# Below this width, the figure is presumed intentional (e.g. the deploy
# snippets the lab author wanted to keep small). The rule does not shrink
# them further or grow them up.
KEEP_AS_IS_BELOW_CM = 13.0

# Tunables for the resize rule.
LANDSCAPE_AR = 1.3   # aspect threshold for "landscape"
LANDSCAPE_CM = 16.0
SQUAREISH_CM = 12.0
PORTRAIT_TARGET_HEIGHT_CM = 11.0
PORTRAIT_MIN_CM = 6.0
PORTRAIT_MAX_CM = 12.0


@dataclass
class Change:
    """A single in-file figure width change."""

    md_file: str
    line: int
    image: str
    aspect: float
    before_cm: float
    after_cm: float


def target_max_width_cm(px_w: int, px_h: int) -> float:
    aspect = px_w / px_h
    if aspect >= LANDSCAPE_AR:
        return LANDSCAPE_CM
    if aspect >= 1.0:
        return SQUAREISH_CM
    width = round(PORTRAIT_TARGET_HEIGHT_CM * aspect, 1)
    return max(PORTRAIT_MIN_CM, min(PORTRAIT_MAX_CM, width))


def pixel_dims_cache() -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for png in SCREENS.glob("*.png"):
        with Image.open(png) as im:
            out[png.name] = im.size
    return out


def line_no_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def process_file(path: Path, pix: dict[str, tuple[int, int]]) -> tuple[str, list[Change]]:
    original = path.read_text(encoding="utf-8")
    changes: list[Change] = []

    def repl(match: re.Match[str]) -> str:
        filename = match.group("file")
        before_cm = float(match.group("cm"))
        if filename not in pix:
            return match.group(0)
        px_w, px_h = pix[filename]
        aspect = px_w / px_h

        # Preserve intentional small figures.
        if before_cm < KEEP_AS_IS_BELOW_CM:
            return match.group(0)

        after_cm = target_max_width_cm(px_w, px_h)
        if abs(after_cm - before_cm) < 0.05:
            return match.group(0)

        changes.append(
            Change(
                md_file=path.name,
                line=line_no_of(original, match.start()),
                image=filename,
                aspect=aspect,
                before_cm=before_cm,
                after_cm=after_cm,
            )
        )

        rest = match.group(0)
        return re.sub(
            r"max-width:[\d.]+cm",
            f"max-width:{after_cm}cm",
            rest,
            count=1,
        )

    new_text = FIGURE_BLOCK_RE.sub(repl, original)
    return new_text, changes


def main(dry_run: bool = False) -> None:
    pix = pixel_dims_cache()
    if not pix:
        sys.exit(f"No screenshots found in {SCREENS} – run convert_heic.py first.")

    all_changes: list[Change] = []
    files_changed = 0
    for md in sorted(DOCS.glob("*.md")):
        new_text, changes = process_file(md, pix)
        if changes:
            all_changes.extend(changes)
            if not dry_run:
                md.write_text(new_text, encoding="utf-8")
            files_changed += 1

    if not all_changes:
        print("No figures needed resizing – everything is already in spec.")
        return

    print(f"{'file':<18} {'line':>4}  {'image':<32} {'aspect':>6}  before -> after")
    print("-" * 92)
    for c in all_changes:
        print(
            f"{c.md_file:<18} {c.line:>4}  {c.image:<32} {c.aspect:>6.2f}  "
            f"{c.before_cm:5.1f}cm -> {c.after_cm:5.1f}cm"
        )

    print(
        f"\n{len(all_changes)} figure(s) resized across {files_changed} file(s)."
        + ("  (dry run – no files written)" if dry_run else "")
    )


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry)
