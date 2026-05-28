#!/usr/bin/env python3
"""Transform pandoc-converted lab guide into mkdocs-ready per-scenario files.

Reads /tmp/ltrsec-conversion/lab-guide-raw.md (pandoc GFM output) and
/tmp/ltrsec-conversion/img_mapping.json (pandoc->HEIC mapping). Writes
cleaned markdown files into docs/ named scenario1.md ... scenario6.md plus
an overview.md with the Learning Objectives + Accessing Devices content.

Transforms applied:
  * Replace `<img src="./extracted-media/media/imageNNN.ext" ... />` blocks
    with mkdocs-friendly figure blocks pointing at
    `assets/screens/<heic-stem>.png` (or `assets/extracted/imageNNN.ext`
    when no HEIC match exists).
  * Unwrap pandoc's quoted-paragraph blockquote prefixes (the leading `> `)
    that pandoc generates for every paragraph; we keep blockquotes only
    for things that were genuinely indented in the source (notes/tips).
  * Collapse the "Table of Contents" pandoc generated from Word's TOC.
  * Strip stray `# ` empty headings pandoc emits for page-breaks.
  * Promote `# Scenario` headings to h1 within their own file (mkdocs
    nav supplies the section titles via .nav.yml).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

RAW_MD = Path("/tmp/ltrsec-conversion/lab-guide-raw.md")
MAPPING_PATH = Path("/tmp/ltrsec-conversion/img_mapping.json")
PANDOC_MEDIA = Path("/tmp/ltrsec-conversion/extracted-media/media")
DOCS_DIR = Path("/home/palugu/LTRSEC-2241-2026/ltrsec-2241-clamer26/docs")
SCREENS_DIR = DOCS_DIR / "assets" / "screens"
EXTRACTED_DIR = DOCS_DIR / "assets" / "extracted"


IMG_TAG_RE = re.compile(
    r"<img\s+src=\"\./extracted-media/media/(image\d+\.(?:png|jpeg|jpg|gif))\""  # capture filename
    r"(?:\s+[^>]*?)?\s*/>",
    re.DOTALL,
)
SCENARIO_RE = re.compile(r"^# Scenario\s+(\d+):\s*(.+?)$", re.IGNORECASE)
EMPTY_HEADING_RE = re.compile(r"^#+\s*$")
BOLD_RE = re.compile(r"^(#+\s+)\*\*(.+?)\*\*\s*$")
# Strip "> " or "    > " (continuation markers pandoc emits inside list items).
BLOCKQUOTE_RE = re.compile(r"^(\s*)>\s?")
# Drop pandoc's bare HTML comments that separate distinct ordered lists; they
# show up as empty paragraphs in mkdocs.
HTML_COMMENT_LIST_BREAK_RE = re.compile(r"^<!--\s*-->\s*$")
# Some Tasks in the source DOCX use bold text instead of a proper heading
# (e.g. `**Task 1: ...**` in a Word callout). After we strip the blockquote
# wrapper, those lines remain plain bold paragraphs; promote them to H2 so
# they appear in the TOC and nav alongside the other Tasks.
BOLD_TASK_RE = re.compile(r"^\*\*(Task\s+\d+:\s*.+?)\*\*\s*$")

# `**Note:** ...` / `**Tip:** ...` callouts (sometimes indented because they
# live inside a list) become `!!! note` / `!!! tip` admonitions, per the
# Cisco Live Labs MkDocs guidelines.
NOTE_CALLOUT_RE = re.compile(
    r"^(?P<indent>\s*)\*\*(?P<kind>Note|Tip|Hint|Important|Warning|Caution|Info)[: ]\*\*\s*(?P<body>.*)$",
    re.IGNORECASE,
)
ADMONITION_KIND_MAP = {
    "note": "note",
    "tip": "tip",
    "hint": "tip",
    "important": "warning",
    "warning": "warning",
    "caution": "warning",
    "info": "info",
}


def load_mapping() -> tuple[dict[str, str], set[str], set[str], dict[str, float]]:
    data = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    mapping = data["mapping"]
    icons = set(data["icons"])
    unmapped = {img for img, _ in data["unmapped"]}
    widths = {k: float(v) for k, v in data.get("widths_in", {}).items()}
    return mapping, icons, unmapped, widths


# Source DOCX uses two effective image-size buckets:
#   - "Small": 6-12 cm wide (most dialogs / inset screenshots)
#   - "Large": 16-16.5 cm wide (full-width screenshots like deploy dialogs)
# Inline UI icons (deploy buttons etc.) are handled by `.inline-icon` styling
# and bypass figure sizing.
MIN_FIGURE_CM = 6.0
MAX_FIGURE_CM = 16.5


def source_width_to_cm(width_in: float | None) -> float | None:
    """Translate the source width (inches) to a display width (cm) within
    the lab guide's documented small-or-large band."""
    if width_in is None or width_in <= 0:
        return None
    width_cm = width_in * 2.54
    return max(MIN_FIGURE_CM, min(MAX_FIGURE_CM, round(width_cm, 1)))


def copy_fallback_images(needed: set[str]) -> None:
    """Copy pandoc-extracted images for unmapped/icon files into assets/extracted/."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for fname in needed:
        src = PANDOC_MEDIA / fname
        dest = EXTRACTED_DIR / fname
        if not src.exists():
            print(f"WARNING: pandoc media missing: {fname}", file=sys.stderr)
            continue
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
            copied += 1
    print(f"Copied {copied} fallback images to {EXTRACTED_DIR}")


def img_replacement(
    filename: str,
    mapping: dict[str, str],
    icons: set[str],
    widths: dict[str, float],
) -> str:
    """Return the markdown replacement for a `<img ...>` reference.

    Preserves the original lab guide's image sizing: small images stay at
    6-12 cm, larger screenshots (deploy dialogs, full-page UI) at ~16 cm,
    each with the 1pt frame applied via CSS in `extra.css`.
    """
    if filename in mapping:
        path = f"assets/screens/{mapping[filename]}.png"
        is_inline_icon = False
    elif filename in icons:
        path = f"assets/extracted/{filename}"
        is_inline_icon = True
    else:
        path = f"assets/extracted/{filename}"
        is_inline_icon = False

    if is_inline_icon:
        # Render icons inline (used in run-on sentences like
        # "Click the Deploy button <icon> on the top right"). `.off-glb`
        # disables the glightbox lightbox per the Cisco Live Labs guideline,
        # and `.inline-icon` shrinks the image to text height.
        return f"![icon]({path}){{ .inline-icon .off-glb }}"

    # Full-width figure for screenshots. Paths are relative to the docs/
    # root because all generated pages live at the top level of docs/.
    width_cm = source_width_to_cm(widths.get(filename))
    if width_cm is None:
        width_cm = MAX_FIGURE_CM  # default to large if source width unknown
    # Inline style on the figure caps the rendered width while letting the
    # image scale fluidly on narrow screens (CSS `max-width: 100%`).
    return (
        f"\n\n<figure markdown style=\"max-width:{width_cm}cm;\">\n"
        f"  ![screenshot]({path}){{ loading=lazy }}\n"
        f"</figure>\n\n"
    )


def replace_images_in_text(
    text: str,
    mapping: dict[str, str],
    icons: set[str],
    widths: dict[str, float],
) -> str:
    def _sub(m: re.Match) -> str:
        return img_replacement(m.group(1), mapping, icons, widths)
    return IMG_TAG_RE.sub(_sub, text)


def unwrap_blockquotes(text: str) -> str:
    """Strip pandoc's automatic `> ` blockquote prefixes from paragraphs.

    Pandoc renders every paragraph after a heading as a blockquote when the
    source DOCX used indented styles. We unwrap them so the markdown reads
    naturally; genuine notes/tips will be re-added later as admonitions if
    needed. We preserve the leading indentation so that list continuations
    (e.g. `    > text` -> `    text`) keep their alignment.
    """
    out_lines: list[str] = []
    for line in text.splitlines():
        out_lines.append(BLOCKQUOTE_RE.sub(r"\1", line))
    return "\n".join(out_lines)


def drop_html_list_breaks(text: str) -> str:
    """Remove pandoc's bare `<!-- -->` paragraphs.

    Pandoc inserts them to force the next ordered list to restart numbering.
    Material for MkDocs renders them as empty paragraphs which looks broken.
    """
    return "\n".join(
        line for line in text.splitlines() if not HTML_COMMENT_LIST_BREAK_RE.match(line)
    )


def strip_empty_headings_and_promote(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        if EMPTY_HEADING_RE.match(line):
            continue
        # Pandoc emits `# **Heading**` from bold styled headings; strip bold.
        m = BOLD_RE.match(line)
        if m:
            line = f"{m.group(1)}{m.group(2)}"
        else:
            # Promote stand-alone `**Task N: ...**` paragraphs (which the
            # Word doc styled as Tasks without a heading level) to H2.
            m_task = BOLD_TASK_RE.match(line)
            if m_task:
                line = f"## {m_task.group(1)}"
        out.append(line)
    return "\n".join(out)


def collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def convert_note_callouts(text: str) -> str:
    """Turn `**Note:** ...` style paragraphs into Material admonitions.

    The Cisco Live Labs MkDocs guideline (slide 24) prescribes:

        !!! note
            See the network topology and follow the guide ...

    Indentation must be 4 spaces (slide 28, "Known Issues #1"). When the
    source callout was inside a list item we preserve its base indentation
    so the admonition stays attached to the list item, and we indent every
    continuation line of the paragraph by `indent + 4` so the whole body
    sits inside the admonition block.
    """
    lines = text.splitlines()
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = NOTE_CALLOUT_RE.match(line)
        if not m:
            out_lines.append(line)
            i += 1
            continue
        indent = m.group("indent")
        kind = m.group("kind").lower()
        body_first = m.group("body").strip()
        admon = ADMONITION_KIND_MAP.get(kind, "note")
        # Collect continuation lines: every subsequent non-blank line is
        # part of the same paragraph in source (pandoc keeps soft-wrapped
        # lines un-merged). Stop at the first blank line.
        body_lines: list[str] = [body_first] if body_first else []
        j = i + 1
        while j < len(lines) and lines[j].strip() != "":
            body_lines.append(lines[j].lstrip())
            j += 1
        out_lines.append(f"{indent}!!! {admon}")
        out_lines.append("")
        body_indent = indent + "    "
        for bl in body_lines:
            out_lines.append(f"{body_indent}{bl}")
        i = j  # let outer loop skip past consumed continuation lines
    return "\n".join(out_lines)


def quote_inline_commands(text: str) -> str:
    """Wrap inline `ping <ip>`, `ssh <ip>`, `traceroute <ip>` snippets in
    backticks (per Cisco Live Labs convention for inline code).

    The source DOCX styles these as **bold** runs; we transform sequences
    like `**ping** **192.168.1.1 -c 5**` into `` `ping 192.168.1.1 -c 5` ``.
    """
    # `**cmd** **args**` pattern - capture only when cmd is a known one.
    cmd_re = re.compile(
        r"\*\*(ping|ssh|traceroute|telnet|nslookup|show|exit)\*\*\s+\*\*([^*]+?)\*\*",
        re.IGNORECASE,
    )

    def _sub(m: re.Match) -> str:
        cmd = m.group(1).lower()
        args = m.group(2).strip()
        return f"`{cmd} {args}`"

    return cmd_re.sub(_sub, text)


def split_scenarios(text: str) -> dict[str, str]:
    """Split into intro + per-scenario sections.

    Returns a dict {slug: content}. Slugs:
      overview, scenario1, scenario2, ..., scenario6.
    """
    sections: dict[str, list[str]] = defaultdict(list)
    current = "overview"
    lines = text.splitlines()
    in_toc = False
    saw_real_intro = False

    for i, line in enumerate(lines):
        # Drop the pandoc TOC: starts with `# Table of Contents` and runs
        # until the next `# ` heading (Learning Objectives).
        if line.startswith("# Table of Contents"):
            in_toc = True
            continue
        if in_toc:
            if line.startswith("# ") and not line.startswith("# Table"):
                in_toc = False
            else:
                continue
        m = SCENARIO_RE.match(line)
        if m:
            n = int(m.group(1))
            title = m.group(2).strip()
            current = f"scenario{n}"
            # Promote to H1, stripping any "**" markdown wrappers.
            title = title.replace("**", "").strip()
            sections[current].append(f"# Scenario {n}: {title}\n")
            continue
        sections[current].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}


def main() -> int:
    mapping, icons, unmapped, widths = load_mapping()
    text = RAW_MD.read_text(encoding="utf-8")

    # Phase 1: Strip pandoc artifacts BEFORE inserting figure blocks so the
    # blockquote unwrap doesn't mangle them.
    text = unwrap_blockquotes(text)
    text = drop_html_list_breaks(text)
    text = strip_empty_headings_and_promote(text)

    # Phase 2: Apply Cisco Live Labs MkDocs conventions.
    text = convert_note_callouts(text)
    text = quote_inline_commands(text)

    # Phase 3: Replace <img> tags using the prepared mapping.
    text = replace_images_in_text(text, mapping, icons, widths)

    # Phase 4: Collapse excess blank lines from the inserted figures.
    text = collapse_blank_lines(text)

    # Phase 4: Slice into per-scenario files. Overview is hand-edited and
    # contains the polished introduction, so skip it to preserve manual edits.
    sections = split_scenarios(text)
    written = []
    for slug, content in sections.items():
        if slug == "overview":
            continue
        out_path = DOCS_DIR / f"{slug}.md"
        out_path.write_text(content.lstrip() + "\n", encoding="utf-8")
        written.append(out_path.name)

    # Phase 5: Stage pandoc-extracted images we still need (icons + unmapped).
    needed = set(unmapped) | set(icons)
    copy_fallback_images(needed)

    print(f"Wrote markdown files: {sorted(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
