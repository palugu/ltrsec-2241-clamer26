# Lab Guide Conversion Scripts

These scripts convert the DOCX source lab guide into mkdocs-ready markdown
with high-quality screenshots from the HEIC source folder.

## One-time setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pillow pillow-heif
pip install -r ../requirements.txt
```

Also install `pandoc` (≥ 3.0) at the system level.

## Pipeline overview

1. **`convert_heic.py`** — Convert every `*.heic` file in `../../Screens/` to a
   web-friendly PNG saved under `../docs/assets/screens/` with lowercase,
   dash-joined names (e.g. `S1.T1.S2.3.heic` → `s1-t1-s2-3.png`).

2. **Pandoc extract** — From the project root, run:

    ```bash
    pandoc -f docx -t gfm \
      --extract-media=./extracted-media \
      ../LTRSEC-2241_2026.docx \
      -o lab-guide-raw.md
    ```

   This produces `lab-guide-raw.md` plus sequential JPEG/PNG fallbacks in
   `extracted-media/media/`.

3. **`build_mapping.py`** — Walks `lab-guide-raw.md`, tracks heading context
   (Scenario / Task / Step), classifies inline icons (< 250 px wide) versus
   full screenshots, and builds the mapping
   `imageN.{png,jpeg}` → `s{N}-t{T}-s{S}-{n}.png`. It also captures the
   original `<img style="width:Xin">` value emitted by pandoc for every
   image — this is what the source DOCX rendered at — so each figure in the
   generated markdown can keep the lab guide's documented sizing (small
   dialogs 6-12 cm, full-width screens ~16 cm). Writes
   `/tmp/ltrsec-conversion/img_mapping.json` with `mapping`, `icons`,
   `unmapped`, and `widths_in` keys.

4. **`process_markdown.py`** — Reads the mapping and the raw markdown, then:
    - Unwraps pandoc's per-paragraph `> ` blockquote prefixes.
    - Removes pandoc `<!-- -->` list-break HTML comments.
    - Promotes stand-alone `**Task N: …**` bold paragraphs to `## Task N: …`.
    - Converts `**Note:** …`, `**Tip:** …` callouts into Material admonitions
      (`!!! note`, `!!! tip`) following the Cisco Live Labs MkDocs guideline
      (4-space indented body, paragraph-aware continuation lines).
    - Wraps inline CLI commands (`ping`, `ssh`, `traceroute`, etc.) that the
      source DOCX styled as bold runs in backtick inline code.
    - Replaces each `<img>` tag with a `<figure markdown style="max-width:Xcm;">`
      block sized from the source DOCX width (clamped to the 6 – 16.5 cm band
      used by the lab guide). Inline UI buttons are emitted instead as
      `![icon](…){ .inline-icon .off-glb }` so they sit inline with text and
      don't trigger glightbox zoom.
    - Splits the document into `scenario1.md` … `scenario6.md`.
    - Copies the remaining pandoc-extracted PNG / JPEG fallbacks to
      `../docs/assets/extracted/` for screenshots that have no HEIC source.

`overview.md`, `topologies.md`, `conclusion.md` and `index.md` are hand-edited
and are **not** overwritten by the pipeline.

## Re-running the pipeline

After updates to the DOCX or Screens folder:

```bash
# 1. Regenerate the HEIC PNGs (skips files already up-to-date)
python scripts/convert_heic.py

# 2. Regenerate the raw markdown
mkdir -p /tmp/ltrsec-conversion && cd /tmp/ltrsec-conversion
pandoc -f docx -t gfm --extract-media=./extracted-media \
  /path/to/LTRSEC-2241_2026.docx -o lab-guide-raw.md
cd -

# 3. Rebuild the image mapping and the markdown files
python scripts/build_mapping.py
python scripts/process_markdown.py
```

## Naming convention

| HEIC source           | Output PNG                | Meaning                                                            |
| --------------------- | ------------------------- | ------------------------------------------------------------------ |
| `S1.heic`             | `s1.png`                  | Scenario 1 network topology diagram                                |
| `S1-Edited.heic`      | `s1-edited.png`           | Updated topology for Scenario 1 (preferred over `s1.png`)          |
| `S1.T1.S2.3.heic`     | `s1-t1-s2-3.png`          | Scenario 1, Task 1, Step 2, picture 3                              |
| `S4.T2.S2.1.2.heic`   | `s4-t2-s2-1-2.png`        | Scenario 4, Task 2, Step 2, picture 1, sub-image 2                 |
| `Pre-configured-*.heic` | `pre-configured-*.png`  | Pre-configured Objects / AC rules diagrams (intro section)         |

## PDF export (mkdocs-with-pdf)

`mkdocs.yml` enables the `with-pdf` plugin by default
(`enabled: !ENV [ENABLE_PDF_EXPORT, true]`). A `mkdocs build` produces both
the HTML site and `site/pdf/document.pdf` (~125 pages, ~46 MB for the full
six-scenario guide). Skip the PDF for quick iteration with
`ENABLE_PDF_EXPORT=false mkdocs build` (or `mkdocs serve`, which the dev
loop reads as `false`).

A couple of mkdocs.yml details are load-bearing for the PDF flow:

- `glightbox` is configured **before** `with-pdf` so the lightbox anchors are
  already in place when with-pdf snapshots each page.
- `docs/stylesheets/extra.css` carries a `@media print` block that forces the
  Material content stack to render. Without it, Material's compiled CSS
  silently clips the combined PDF document down to ~32 pages.

## Image presentation

All figures are wrapped in `<figure markdown style="max-width:Xcm;">`. The CSS
in `docs/stylesheets/extra.css` then:

- gives every screenshot a **1 pt** solid border (matching the printed lab
  guide),
- keeps the figure responsive (`width: 100%`, `max-width: 100%`),
- uses a lighter border color in dark mode for visibility, and
- strips the border from inline UI icons via the `.inline-icon` class.

### Figure sizing (`resize_figures.py`)

`process_markdown.py` initially seeds `max-width` from the DOCX width. That
preserves the source intent but produces an uneven rhythm in the rendered
HTML/PDF (portrait dialog screenshots inflate to full page width). After the
markdown is generated, run

```bash
python scripts/resize_figures.py
```

to normalize every `<figure>` based on the underlying PNG's pixel aspect
ratio:

- **landscape** (aspect ≥ 1.3) → `max-width: 16cm`
- **square-ish** (1.0 ≤ aspect < 1.3) → `max-width: 12cm`
- **portrait** (aspect < 1.0) → target rendered height ≈ 11 cm, so
  `max-width = round(11 × aspect, 1)` clamped to 6–12 cm

Any figure currently below 13 cm is treated as intentional ("deploy" / inline
snippet) and left alone. The script is idempotent — running it twice is a
no-op. Pass `--dry-run` (or `-n`) to preview changes without writing.

To re-tune the size policy edit the constants near the top of
`scripts/resize_figures.py` (`LANDSCAPE_CM`, `SQUAREISH_CM`,
`PORTRAIT_TARGET_HEIGHT_CM`, etc.).
