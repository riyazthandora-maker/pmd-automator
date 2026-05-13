# Skill User Guide — Design Specification

> A reusable recipe for building A4 print-ready user manuals in HTML for **any single skill in the Agent Development Kit (ADK)**. Hand this spec — together with your skill's content outline — to a designer, an agent, or yourself, and you'll produce a manual that's visually consistent with every other ADK skill guide.

---

## 1. Purpose & Audience

This spec describes how to build a **multi-page, A4 portrait, print-ready HTML manual** for a single ADK skill that:

- Renders identically on screen and on paper (210 × 297 mm pages with crisp page breaks).
- Carries the **DEWA visual identity** (primary green `#007560`, secondary blue, structured typography).
- Scales gracefully from a small 8-page reference to a 30-page multi-section guide.
- Doubles as a **PDF source**: a `*-print.html` sibling auto-triggers `window.print()` so users can save as PDF in one step.

**Audience:** internal DEWA stakeholders — the people who will operate, configure, or extend the skill. Tone: instructional, formal-but-warm, structured. Treat the reader as a competent practitioner, not a beginner.

**Scope:** one skill per guide. If your skill is a meta-skill that orchestrates several others, document each child skill in its own guide and cross-reference them.

---

## 2. Document Anatomy

Every guide is built from the same set of page archetypes. **Pick the ones you need; skip the rest.** A short reference guide may use only Cover · Contents · 4–6 content pages · Sign-off. A full multi-part guide can layer on opener pages and a cheat sheet.

### Page archetypes

| Archetype | When to use | Notes |
|-----------|-------------|-------|
| **Cover** | Always (page 1) | Org chain, title, descriptor, three-pillar summary, meta row |
| **Table of Contents** | Always (page 2) | Two-column TOC grouped by part |
| **Foundation Opener** | When a guide has 2+ parts | Big numeral `00`, headline, descriptor, three pillar cards |
| **Foundation pages** | When the skill has shared concepts | Architecture diagram, invocation, scope, glossary |
| **Part Opener** | One per major section (Part 1, 2, 3 …) | Numeral in part colour, accent bar on left edge |
| **Part content pages** | Bulk of the guide | Prerequisites, configuration, walkthrough, reference |
| **Cheat Sheet** | When the skill has many commands/inputs | Three-column quick-reference cards |
| **Sign-off** | Always (last page) | Revision history, approver names, classification |

### Recommended shapes

| Guide size | Total pages | Layout |
|------------|-------------|--------|
| **Compact** | 8–12 | Cover · TOC · 4–8 content pages · Sign-off |
| **Standard** | 16–22 | Cover · TOC · Foundation (3–4 pages) · Single-part content (10–14 pages) · Cheat Sheet · Sign-off |
| **Multi-part** | 24–30 | Cover · TOC · Foundation Opener · Foundation pages · Part 1 (Opener + content) · Part 2 (Opener + content) · Part 3 (Opener + content) · Cheat Sheet · Sign-off |

**Page rhythm matters more than page count.** Every spread should feel intentional, never padded.

---

## 3. Page Geometry

```
┌──────────────────────────────── 210 mm ────────────────────────────────┐
│  HEADER  (height 18 mm, padding 8mm 16mm 0)                            │ ▲
│  ────────────────────────────────────────────────────────────────────  │ │
│                                                                        │ │
│                                                                        │ │
│                                                                        │ │
│   PBODY  (top:18mm  left:16mm  right:16mm  bottom:14mm)               │297mm
│   — all primary content lives here —                                   │ │
│                                                                        │ │
│                                                                        │ │
│  ────────────────────────────────────────────────────────────────────  │ │
│  FOOTER  (height 14 mm, padding 0 16mm)                                │ ▼
└────────────────────────────────────────────────────────────────────────┘
```

- Outer page: `width:210mm; height:297mm; overflow:hidden; page-break-after:always`.
- Body absolutely positioned with `top:18mm; left:16mm; right:16mm; bottom:14mm` so header and footer never collide with content.
- Cover and part-opener pages skip the header/footer; they use full-bleed `.part-opener { position:absolute; inset:0 }`.

---

## 4. Design Tokens

Drop this `:root` block at the top of every guide. **Do not invent new colours** — pick from these tokens and let part dividers do the differentiation.

```css
:root{
  /* Brand primaries */
  --primary:           #007560;   /* DEWA green */
  --primary-variant:   #004937;
  --primary-tint:      #D9EAE7;
  --primary-tint-soft: #E5F1EF;

  /* Secondary accents (used for sub-parts, callouts, info chips) */
  --accent-blue:       #0B7BC1;
  --accent-blue-tint:  #DAEBF6;
  --accent-orange:     #E26D5A;
  --accent-bronze:     #A2511A;

  /* Status */
  --error:             #B00020;
  --error-tint:        #F3D9DE;
  --warn-bg:           #FCF5E7;

  /* Neutrals */
  --grey-100:#EFEFF1; --grey-150:#F2F3F3; --grey-200:#D7D7DF;
  --grey-300:#BDBDBD; --grey-600:#6F6F6F; --grey-700:#4D4D4D; --grey-900:#222222;
  --bg:#FFFFFF;       --ink:#222222;

  /* Type scale (point-based for print fidelity) */
  --t-h1:28pt;  --t-h2:17pt;  --t-h3:12pt;  --t-h4:10.5pt;
  --t-body:9.5pt; --t-small:8.5pt; --t-caption:8pt; --t-mono:8.2pt;

  /* Stacks */
  --font: -apple-system, "SF Pro Display","SF Pro Text","Helvetica Neue", system-ui, sans-serif;
  --mono: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
}
```

> **Density variant for sample-heavy or visually-rich guides:** drop the type scale by ~1pt — `--t-h1:26pt; --t-h2:16pt; --t-body:9pt; --t-small:8pt; --t-caption:7.6pt; --t-mono:7.8pt` — and shorten `line-height` to 1.42. This buys the room you need for big preview canvases, sample cards, and four-column anatomy grids without overflowing pages.

For **a dedicated sub-part with its own identity** (e.g. a platform-specific section), pick a one-off colour and apply it inline through modifier classes (`.ph.<part>`, `.part-opener.<part>`). Don't add part-specific colours to `:root` unless they're shared across multiple guides.

### Semantic colour roles

| Role | Token | Where it appears |
|------|-------|------------------|
| Primary brand | `--primary` | Section numbers, headers, primary buttons, table headers, eyebrow text |
| Default section accent | `--primary` | Header strip, accent bar, opener numeral |
| Alternate section accents | `--accent-blue`, custom one-offs | Per-part chrome (chip, accent bar, numeral) |
| Body ink | `--grey-900` | All body copy |
| Secondary ink | `--grey-700` | Description rows, do/don't body copy, captions |
| Muted | `--grey-600` | Captions, footers, tertiary labels |
| Hairlines | `--grey-100` / `--grey-200` | Dividers, table borders |
| Tinted panels | `--primary-tint-soft` | Success callouts, soft highlights, validation feedback chips |
| Code background | `#0F1A18` (dark) / `--grey-150` (light) | `.code` blocks |

---

## 5. Typography

**One sans family.** Use the system stack (`-apple-system, "SF Pro Display"…`) — no Google Font imports, no Inter, no Roboto. The result is sharp on macOS/iOS and falls back gracefully on Windows/Linux.

| Style | Class / Element | Size | Weight | Notes |
|-------|-----------------|------|--------|-------|
| Cover headline | `.cover h1` | 48pt | 700 | `letter-spacing:-0.02em`, `line-height:1` |
| Cover headline em | `.cover h1 .em` | inherit | 700 | Coloured `--primary`, often a separate display block |
| Part opener numeral | `.part-opener .num` | 120pt | 800 | In part colour; `letter-spacing:-0.04em` |
| Part opener headline | `.part-opener h1` | 42pt | 700 | `line-height:1.05` |
| H1 (page title) | `h1.t` | 28pt (or 26pt dense) | 700 | `letter-spacing:-0.01em` |
| H2 | `h2.t` | 17pt (or 16pt dense) | 700 | `margin:0 0 5mm`; auto top-margin via sibling rules |
| H3 (section) | `h3.t` | 12pt (or 11.5pt dense) | 600 | `margin:0 0 3mm` |
| Body | `p`, `.lede` | 9.5pt / 11pt | 400 / 500 | `line-height:1.5`–`1.55` |
| Small / caption | `--t-small`, `--t-caption` | 8.5pt / 8pt | varies | UI labels, meta text |
| Eyebrow | `.eyebrow`, `.toc-part` | 8pt | 700 | `letter-spacing:.18em`, uppercase, primary colour |
| Mono | `--mono` | 8.2pt | 400 | Inline `code`, `.code` blocks, `.tool` chips, KPI numerals when designed |

**Vertical rhythm:** Body is 9.5pt × 1.5 = ~14pt baseline. Major section breaks are `margin-top:8mm`; subsection breaks `6mm`. The selector `h2.t + .panel { margin-top:0 !important }` collapses the gap when a heading sits directly above a block, keeping things tight.

**KPI numerals** can be set in monospace (`font-family:var(--mono)` on `.kpi .v`) to evoke "data" rather than "headline". Pick one mode per guide and stick with it.

---

## 6. Component Library

Components are grouped: **(A) chrome & structure**, **(B) content blocks**, **(C) showcase components** (for guides that document UI artefacts, prompts, or generated outputs).

---

### A. Chrome & Structure

#### A.1 Header / Footer (`.ph` / `.pf`)

- Header height **18 mm**, footer **14 mm**, both with 16 mm horizontal padding.
- Header: `[brand chip] [doc version + month]`. Brand chip = an 8–10 px coloured square (`.ph .brand .dot` or pseudo-element) + skill name.
  - Modifier classes (e.g. `.ph.<part-key>`) swap the chip colour per part.
- Footer: `[classification text] [Page NN / TT]`. Page numerals use `font-variant-numeric:tabular-nums`.

#### A.2 Cover (`.cover`)

- **Left rail** (`.rail`): 18 mm wide solid primary green, with a circular **version badge** at top and a vertical org-chain caption at bottom (`writing-mode:vertical-rl; transform:rotate(180deg)`).
- **Cover body** (`.cover-body`): logo + org name → headline (48pt) → eyebrow with hairline pip → descriptive sub → department breadcrumb chain → three-pillar summary → meta row (Document / Released / Classification).
- The **department chain** uses `›` separators in `--grey-300` and bolds the current dept in `--primary`.
- The cover headline can interleave a coloured `<span class="em">` for emphasis (e.g. a file-name, a sub-title, a year).

#### A.3 Table of Contents (`.toc-grid` / `.toc-row`)

- Two columns, each row a 22px / 1fr / auto grid: number → title → page.
- Grouped by `.toc-part` headings — uppercase, letter-spaced, with a 1px tinted underline matching the part colour.
- Numbering is part-prefixed: `1.1 / 1.2 / 1.3 …` for Part 1, `2.1 / 2.2 …` for Part 2, etc.
- For wider, single-row part headings, `.toc-part` can span both columns: `grid-column:1 / -1`.

#### A.4 Part Opener (`.part-opener`)

- Full-bleed white page, **8 mm vertical accent bar** glued to the left edge in the part colour.
- Stack: huge numeral (`120pt`) → headline (`42pt`) → descriptor paragraph (`13pt`) → `.pillars-row` of three feature cards anchored to the bottom (`margin-top:auto; padding-bottom:12mm`).
- The `.po-body` flex column carries `padding-top:32mm` so the giant numeral sits with deliberately airy breathing room from the top of the page. This matches the line-box position of `h1.t` on content pages (which sits at `18mm` header + `14mm` `.pbody` padding-top = 32mm from page top), giving the entire document one consistent "content starts here" baseline.
- No header, no footer, no page number — these pages are pure dividers.

#### A.5 Compact Part Divider (`.partdiv`)

- An **inline** part divider for guides that don't need a full opener page: a single dark-green pill at the top of a content page reading `[01] Foundation` or `[02] Configuration`.
- Solid `--primary-variant` background, white uppercase letter-spaced text, with a monospaced number chip (`.p`) sitting on rgba-white.
- Use when you have 2–4 sub-parts inside a single `.pbody` and don't want to spend a full page on a divider.

#### A.6 Section Number (`.section-no`)

- 34×34 rounded square in `--primary` with a white numeral. Used at the start of major sections.
- Variants:
  - `.section-no.phase` — wider: `[PHASE] [N]` in `--primary-variant` background.
  - `.section-no.platform` — same shape, used for `[PLATFORM] [N]` or any other typed sequence.
  - **Add your own** with a custom prefix label (`.section-no.<keyword>`) when your skill has its own ordering vocabulary.

#### A.7 Group Header (`.group-hd`)

- An **in-page subsection lead-in** that sits above a block of cards or item rows.
- Layout: left side is a monospaced primary-coloured number (`.num`, 11pt) + a 13pt bold title (`.ti`); right side is an uppercase letter-spaced caption (`.ct`) like `04 INPUTS` or `12 STEPS`.
- Lighter than `h2.t`, more structured than just bold text — perfect for "Section name · count" framing.

---

### B. Content Blocks

#### B.1 Tables (`.tbl`)

- Header row: solid `--primary` background, white uppercase 8pt labels with `.06em` tracking.
- Body rows: 5.5px vertical padding, alternating `#FAFAFB` zebra, hairline bottom borders.
- **Tag pill** `.tbl .tag`: 2px / 8px pill in `--primary-tint` with `--primary-variant` text. Variants `.tag.b` (blue), `.tag.o` (orange), `.tag.r` (red) for status colour-coding.
- Inline `code` inside cells gets a soft grey chip.

#### B.2 Callouts (`.callout`)

Four flavours, each a coloured-background card with an 18×18 round icon left-side:

| Variant | Background | Icon background | Use for |
|---------|------------|-----------------|---------|
| `.success` | `--primary-tint-soft` | `--primary` | Confirmations, "you're done" notes |
| `.info` | `--accent-blue-tint` | `--accent-blue` | Tips, neutral context |
| `.warn` | `--warn-bg` | `#C28B14` | Cautions, recoverable mistakes |
| `.danger` | `#FBE9EC` | `--error` | Hard errors, blocking issues |

Use sparingly — one callout per page max. They lose impact when stacked.

#### B.3 Code Blocks (`.code`)

- **Dark variant**: `#0F1A18` background, `#E8F1EE` text, soft mint and amber syntax highlighting via `.c` (comments), `.k` (keywords), `.s` (strings), `.ok` / `.bad`, `.lab`, `.dim`. Use for terminal output, command transcripts, sample logs.
- **Light variant** `.code.light`: grey background for non-terminal snippets (config files, JSON, structured data).
- Always wrap with `white-space:pre-wrap; word-break:break-word` so long lines reflow within the 178 mm pbody width.

#### B.4 Phase Strip (`.phase-strip`)

- Equal-width grid of 5–7 cells (`grid-template-columns:repeat(N,minmax(0,1fr))`).
- Each cell `.ps`: small caption number → label. Active cell uses solid `--primary` background with white text.
- Use to show progression through a multi-step lifecycle, workflow, or pipeline (e.g. phases 0–6 of an automated process).

#### B.5 Architecture Diagram (`.arch`)

- Same equal-grid mechanism as the phase strip.
- Cell variants `.brain` (solid primary), `.target` (tinted) plus your own per-part variants tell the reader which layer is which.
- `.lbl` is a tiny uppercase caption (8pt, `.1em` letter-spacing); `.nm` is the 10pt bold label.
- **Always** set `overflow-wrap:break-word` on `.nm` — long technology names otherwise overflow narrow cells.

#### B.6 KPIs (`.kpis` / `.kpi`)

- Four-column grid of stat cards: huge 22pt primary number + small grey label.
- Use 3–6 numbers max; more dilutes impact. Only show numbers you can defend.
- Optional: set `.kpi .v` in `--mono` for a "data display" feel.

#### B.7 Steps (`.steps` / `.step`)

- Vertical stack of bordered rows, each with a 24px round badge (1, 2, 3 …) followed by an H5 title and a one-line description.
- Use for ordered procedures of 3–8 steps. Beyond that, switch to a numbered table.

#### B.8 Tools / Commands Grid (`.tools-grid`)

- Three-column grid of monospace chips, each with a coloured dot. Useful for listing tool names, command identifiers, or config keys at a glance.

#### B.9 Pillars (`.pillar`)

- Card with a 30×30 tinted icon box, h4 title, and one-line description.
- Three to four pillars per row works best. Add modifier classes to vary the icon background colour per pillar when they represent distinct things.

#### B.10 Cheat Sheet (`.cheat`)

- Three-column grid of `.card`s, each with an iconified h4 and a tight `<ul>` of one-line tips.
- Card titles get an 18×18 rounded-square icon in `--primary-tint` next to the heading.

#### B.11 Tree / File Tree (`.tree` / `.file-tree`)

- Monospaced block for file structures, directory listings, or hierarchical data, rendered with `white-space:pre`.
- `.f` highlights filenames in `--primary-variant`; `.c` greys out comments/annotations; `.b` (`.file-tree` only) highlights binary/asset references in `--accent-bronze`.
- `.tree` is the simpler 3-class version; `.file-tree` adds the bronze accent for asset paths.

#### B.12 Pill / Tag (`.platform-pill`)

- Inline chip showing which scope, platform, persona, or category a piece of content belongs to.
- 6×6 round dot + uppercase letter-spaced label. Drop into headings to disambiguate.
- **Define your own variants** as your skill needs them (e.g. `.input`, `.output`, `.optional`, `.beta`). Each variant pairs a tinted background with a darker foreground. Don't exceed 4–5 variants per guide — more becomes noise.

#### B.13 Lists

- `ul.clean`: minimal — disc bullets, 18px indent, 3px row spacing.
- `ul.dewa`: bespoke — square primary-coloured bullets (`::before` 8×8 rounded square in `--primary`), no default marker.
- `.lede`: oversized opening paragraph, 11pt / 1.55, used right under H1.
- `.muted`: grey body text for secondary explanations.

#### B.14 Item Rows (`.item-rows` / `.ir`)

- A clean **2-column key/value list**: 38% bold name, 62% description, hairline divider between rows.
- Replaces the old `<dl>` pattern. Used for input/output reference lists, parameter tables that don't need column headers, glossary entries.
- Tighter than a table, denser than a panel grid — lives between them.

---

### C. Showcase Components

Use these when the **subject of the guide is itself an artefact** the skill produces — UI screens, prompts, generated documents, configurations, structured outputs. They're more illustrative than the content blocks above. Skip this whole family if your skill is a process / workflow tool.

#### C.1 Filename Chip (`.mdfile`)

- An **inline filename badge** styled like `[· filename.ext]` — small monospaced pill in `--primary-tint-soft` with a 6×6 primary square pseudo-element to its left.
- Use whenever you reference a literal file by name in body copy. Distinct from inline `code` because it carries semantic weight: "this is the source-of-truth file".
- 9pt mono, 600 weight, 5px corner radius. Don't overuse — once per page is plenty.

#### C.2 Sample Card (`.sample`)

- A **two-column showcase** for an example screen / artefact / output: left column (`.bd .pr`, 50%) is a description on a `#FAFAFB` background; right column (`.bd .rs`, 50%) is the visual, on a deep dark background (`#0F1A18` with a soft radial primary tint).
- Header `.hd` runs across the top in `--grey-150` with the sample name (`.nm`, 11pt bold, regular case) on the left and a small uppercase index/caption on the right.
- The visual canvas (`.pv`) holds either a vector frame (`svg.frame`) or a raster image (`img.frame-img`); both are `drop-shadow`-cast for depth. Variant `.pv-img` switches the canvas to white for screenshot/photo previews.
- Mono labels in the corners (`.lab` bottom-left, `.ps` top-right) give the previews "exhibit number / metadata" texture.

#### C.3 Sample Grid (`.sample-grid`)

- A **single-column stack** of `.sample` cards. Each card spans full pbody width with its internal Prompt / Output split (50 / 50) preserved inside.
- Inside `.sample-grid`, `.sample` is auto-shrunk: smaller padding, 8pt body copy, lighter headers (5/10px padding), preview canvas constrained to 300–340px tall.
- Cards are noticeably shorter than full-width standalone `.sample` cards because the wider Prompt/Output sections wrap less text. In practice, **4 cards comfortably fit on one A4 page** with ~80mm of slack at the bottom for typical agent-output content.
- Use this whenever you have 3+ examples that benefit from being read sequentially top-to-bottom rather than scanned as a 2×2 grid. For 1–2 examples → full-width standalone `.sample` cards.

#### C.4 Anatomy Grid (`.anatomy`)

- A **4-column breakdown** of the parts of a structured artefact (e.g. the four sections of a generative prompt, or the four fields of a configuration schema).
- Each `.a` card carries: an uppercase primary-coloured `.k` label, a 1-line `.d` description, and an `.e` example block in mono on a grey background.
- Perfect for "anatomy of X" diagrams: prompt anatomy, file-format anatomy, response anatomy, request anatomy.

#### C.5 Validation Checks (`.checks` / `.check`)

- A **3-column row of "what we verify" cards**, each with a number badge (`.num`) tucked into the top-left corner spilling above the card border, an h5 title, a description, and a feedback example (`.fb`) in tinted-soft primary.
- Use when you need to enumerate the 3–6 quality gates the skill applies before declaring an output valid.
- Don't use for ordered procedures — that's `.steps`. `.checks` is for **parallel** verification criteria.

#### C.6 Six-Card Grid (`.six-grid` / `.six-card`)

- A **3 × 2 grid of compact reference cards**, each carrying a uppercase number caption (`.num`), a 10.5pt h5 name, a small monospaced filename or identifier (`.file`), and a 1-line description.
- Designed for "one card per item" reference pages where ~6 things need equal weight.
- Smaller and denser than `.pillar` cards; lighter than `.cheat .card`.

#### C.7 Do / Don't (`.dodont`)

- A **2-column rule card pair**: left card has a primary-green left border (`.do`), right card has an error-red left border (`.dont`).
- Each carries a coloured h5 ("Do" / "Don't") and a single short paragraph of body copy.
- Use to crystallise an opinionated rule on a page (e.g. "Do reference inputs by name" / "Don't hard-code values"). One pair per topic; don't stack multiple pairs.

#### C.8 Spec Band (`.spec-band`)

- A **horizontal band of label/value pairs** at the very top of a section, summarising its key facts in one line: e.g. `STATUS · production · VERSION · 4.0 · LAST UPDATED · April 2026`.
- Light grey background, 8mm tall, uppercase labels in `--grey-600`, bold values in `--grey-900`, `·` separators in `--grey-300`.
- Wraps gracefully on small content widths. Use for "at-a-glance metadata" framing on platform / module / sub-skill sections.

---

## 7. Layout Patterns

A handful of grid recipes carry most pages. Memorise these.

| Pattern | CSS | Use case |
|---------|-----|----------|
| `.grid-2` | `grid-template-columns:1fr 1fr; gap:12px` | Side-by-side panels |
| `.grid-3` | `repeat(3,1fr); gap:12px` | Three-up cards |
| `.grid-4` | `repeat(4,1fr); gap:10px` | Token grids, anatomy rows |
| `.row` + `.col` | flex with `gap:14px` | When children need different intrinsic widths |
| `.kpis` | `repeat(4,1fr); gap:10px` | Stat strip |
| `.phase-strip` | `repeat(N,minmax(0,1fr))` | Linear progress / phases |
| `.arch` | `repeat(N,minmax(0,1fr))` | System architecture |
| `.cheat` | `repeat(3,1fr); gap:10px` | Quick-reference cards |
| `.sample-grid` | `1fr; gap:8px` | Single-column stack of `.sample` showcase cards |
| `.anatomy` | `repeat(4,1fr); gap:8px` | 4-piece structural breakdown |
| `.checks` | `repeat(3,1fr); gap:10px` | 3 parallel validation criteria |
| `.six-grid` | `repeat(3,1fr); gap:8px` | 3×2 dense reference cards |
| `.dodont` | `repeat(2,1fr); gap:10px` | Do / Don't card pair |

`minmax(0,1fr)` is critical for any equal-width track — without the `0` floor, long words inflate cells and break the grid.

---

## 8. Print & PDF Pipeline

Every guide ships **two HTML files**:

1. `<Skill Name> - User Manual.html` — the canonical viewer file. Padded grey background (`#E9EAEC`), drop shadows on each page so it reads like a stack of cards in the browser.
2. `<Skill Name> - User Manual-print.html` — a copy with a `@page { size:A4 portrait; margin:0 }` rule, an `@media print` block that strips the grey background and shadows, and an inline auto-print script:

```html
<script>
(async () => {
  try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
  if (document.readyState !== 'complete')
    await new Promise(r => window.addEventListener('load', r, { once:true }));
  setTimeout(() => window.print(), 500);
})();
</script>
```

The print sibling is what ops opens to "Save as PDF". Don't ship just the canonical file — Chrome's default print of the unpadded version is letterboxed and ugly.

**Print rules** to include:

```css
@page { size:A4 portrait; margin:0; }
@media print {
  html, body { background:#fff !important; padding:0 !important; margin:0 !important; }
  .page {
    margin:0 !important; box-shadow:none !important;
    page-break-after:always; break-after:page; break-inside:avoid;
  }
  .page:last-child { page-break-after:auto; break-after:auto; }
  *, *::before, *::after {
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
    color-adjust:exact !important;
  }
}
```

`print-color-adjust:exact` is mandatory — without it Chrome strips background fills (table headers, callouts, code blocks all turn white).

---

## 9. Required Content per Page Type

A skill guide isn't done until each page type carries its required content. Use this as a checklist when scoping.

### Cover (always required)
- DEWA logo + organisation name
- Skill name (the headline)
- One-sentence skill descriptor (the sub)
- Department breadcrumb chain ending at your team
- Three-pillar summary of what the skill does (one verb each: e.g. "Connect / Process / Deliver")
- Meta row: Document version · Released date · Classification

### Table of Contents
- One row per major section, with prefixed numbering (`1.1`, `1.2` …)
- Page numbers right-aligned, `font-variant-numeric:tabular-nums`
- Grouped under `.toc-part` headings if the guide has 2+ parts

### Foundation pages (when used)
- **Architecture / mental model** — how the skill fits into the broader agent ecosystem (`.arch`)
- **Invocation** — how the user activates the skill (commands, triggers, chat phrases)
- **Inputs & outputs** — what the skill consumes and what it produces (use `.item-rows` or `.tbl`)
- **Lifecycle / phases** — the high-level steps the skill runs through (`.phase-strip`)

### Part content pages
At minimum, every part should cover:
- **Prerequisites** — accounts, permissions, hardware, tools (`.tbl` or `.item-rows`)
- **Configuration** — files, fields, defaults (`.code.light` for the file, `.tbl` for fields)
- **Walkthrough** — phase-by-phase or step-by-step (`.steps`, `.phase-strip`, or both)
- **Reference** — exhaustive parameter / command list (`.tbl`)
- **Troubleshooting** — at least 3 common failure modes and remedies (`.callout.warn` or `.tbl`)

### Cheat Sheet (when used)
- One card per part of the guide (or per top-level concept), each with 4–8 bullet shortcuts
- Use `.cheat .card` with iconified h4

### Sign-off (always required)
- Document version + release date
- Approver names with roles
- Classification level (Internal / Confidential / Public)
- Revision history table (date · version · author · summary)

---

## 10. Authoring Checklist

Run through this before declaring a guide done.

### Content
- [ ] Cover has org chain breadcrumb ending in **bold primary** for the current department.
- [ ] TOC numbers match in-page numbers exactly.
- [ ] Every part opener has the **same shape**: numeral → headline → descriptor → 3 pillars.
- [ ] Cheat sheet (if used) covers every part.
- [ ] Sign-off page lists actual approvers (no `TBD`).
- [ ] Every page type meets its content checklist (§9).

### Layout
- [ ] No page overflows: `body.scrollHeight <= body.clientHeight + 1` for every `.pbody`.
- [ ] No long monospace string causes a grid cell to widen — confirm `minmax(0,1fr)` is in place.
- [ ] Tables fit within 178 mm width. Wide ones use `<th style="width:..%">` to lock columns.
- [ ] Code blocks reflow (`white-space:pre-wrap` or a hard line break in source).
- [ ] No callout, panel, or table is split across a page break.
- [ ] Sample cards (if used) keep their preview canvas under ~248px tall on full-width, ~340px on grid layouts.

### Visual
- [ ] Only DEWA tokens used (no random hex codes inline).
- [ ] System sans only — no Google Fonts.
- [ ] Header chip colour matches the part the page belongs to.
- [ ] Page number `Page NN / TT` matches the actual total.
- [ ] At most one callout per page; at most one Do/Don't per topic.

### Print
- [ ] `*-print.html` exists, auto-prints, and produces a PDF with no clipping.
- [ ] Save-as-PDF sample reviewed at 100% zoom.

---

## 11. Authoring Workflow

1. **Pick your shape (§2).** Compact, Standard, or Multi-part.
2. **Outline the TOC first.** Decide the parts, decide the page count per part, write the section numbers. The TOC is your contract.
3. **Stub every page.** Create `<section class="page" data-screen-label="NN Title">` shells with header + footer + an empty `<div class="pbody">`. This gives you a complete page count immediately and surfaces overflow problems early.
4. **Fill in content top-to-bottom**, not section-by-section. Catch cross-references as you go.
5. **Run an overflow audit** after every major fill: pages whose `.pbody` scrolls have too much content.
6. **Last pass**: replace any placeholder names, regenerate the cheat sheet from the real content, set the document classification, fill the revision history.
7. **Spawn the print copy** by `cp <Guide>.html <Guide>-print.html` and add the `@page` + auto-print snippet at the top of the `<style>` block.

---

## 12. Anti-patterns

Things to avoid because they've broken past guides:

- **Don't use `repeat(N, 1fr)` without `minmax(0, 1fr)`** — long content blows out columns.
- **Don't stack two callouts on one page** — they fight each other for attention.
- **Don't put 12+ rows in one table.** Split into two or move into a 2-column grid of cards.
- **Don't add a page footer to part-opener pages.** The numeral and accent bar are the only chrome those pages need.
- **Don't introduce new colours** for "just this one section". Use existing tokens or add a token to `:root`.
- **Don't rely on `<br>` for layout.** If you find yourself adding `<br><br>` to push a block down, switch to `margin-top:auto` inside a flex column.
- **Don't ship a single canonical file as the PDF source.** Always produce the `*-print.html` sibling.
- **Don't mix the standard type scale with the dense one** within a single guide. Pick one mode at the start.
- **Don't put `.sample` cards full-width on more than 2–3 pages.** If you have many examples, switch to `.sample-grid`.
- **Don't add a new pill variant per category mention.** Reuse existing variants; add a new one only if it appears 3+ times across the guide.
- **Don't write content that depends on screen behaviour** (hovers, animations, links). The PDF is the canonical artefact.

---

## 13. File Naming Conventions

```
<Skill Name> - User Manual.html         ← canonical viewer (self-contained)
<Skill Name> - User Manual-print.html   ← auto-print sibling (self-contained)
```

Both files inline the brand logo as SVG (see §16.1) along with all CSS, fonts (system stack only), and helper scripts directly in the HTML. No `assets/` folder, no external host, no network dependency — each guide ships as a single self-contained file. If you need to add product imagery (screenshots, diagrams), inline them as base64 `data:` URIs so the deliverable stays equally portable.

Keep the on-disk filename close to the document's cover title. Future readers find files by scanning a folder, not by reading metadata. Use the skill's full name — not an internal codename or abbreviation.

---

## 14. Choosing Your Component Set

Not every guide needs every component. Match the component family to the skill's character:

| Skill character | Use these component families | Lean on |
|-----------------|------------------------------|---------|
| **Process / workflow skill** (automates a multi-step procedure) | A (chrome) + B (content blocks) | Phase strip, KPIs, steps, tools grid, callouts, tables |
| **Generative / design skill** (produces visual or structured artefacts) | A + B + **C (showcase)** | Sample cards, anatomy, checks, do/don't, filename chips |
| **Reference / catalogue skill** (enumerates many items) | A + sample-grid + item-rows + group-hd + spec-band | Light on B; the content *is* the catalogue |
| **Hybrid (process + generative)** | All three — but lean on the **dense type variant** | Mix freely; keep page count under 30 |
| **Diagnostic / observability skill** (reports on system state) | A + B (heavy on tables and callouts) | Tables, callouts (especially `.warn` / `.danger`), KPIs |

When in doubt, start with the process-style set (A + B) and only pull in C components when the content is fundamentally about *artefacts the skill produces* (screens, prompts, files, structured outputs) rather than *steps the user follows*.

---

## 15. Skill Guide Variants — Quick Reference

| Skill type | Recommended shape | Page-count target | Notes |
|------------|-------------------|-------------------|-------|
| Internal automation skill (1 platform, 1 flow) | Compact | 8–12 | Cover · TOC · 4–8 content · Sign-off |
| Single-product skill with config | Standard | 16–22 | Add Foundation pages and a Cheat Sheet |
| Multi-platform / multi-target skill | Multi-part | 24–30 | Use Part Openers per platform |
| Design / generative skill | Standard or Multi-part | 18–28 | Lean heavily on §6.C showcase components |
| Catalogue / reference skill | Standard | 16–22 | Pages dominated by `.item-rows`, `.tbl`, `.six-grid` |

---

*This spec is a living document. When a new skill needs a component none of the above covers, add it here first, then use it. Don't fork the system; extend it.*

---

## 16. Brand Assets

The DEWA brand mark is **inlined as SVG** directly in every guide. No external URL, no `assets/` folder, no network dependency — the manual stays a single self-contained file that renders identically online, offline, and in print.

### 16.1 DEWA logo (canonical inline SVG)

Paste this block into the cover page's `.cover-org` slot. Display size is controlled by the `.cover-org .logo { width:42px; height:42px }` CSS rule (see §17). The `viewBox` is `0 0 668 671` — the artwork's native canvas — so the gradient stops scale correctly at any rendered size.

Gradient IDs are namespaced with a `dewa-` prefix so they cannot collide with other elements in the document. If you embed multiple instances of the mark on a single page (rare), suffix the IDs further (`dewa-paint0-cover`, `dewa-paint0-footer`, etc.).

```html
<svg class="logo" viewBox="0 0 668 671" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="DEWA">
  <path d="M10.1124 305.569C10.1124 298.585 10.6179 291.713 11.0673 284.841C15.9354 217.814 44.5437 154.743 91.7252 107.017C174.308 23.6863 300.184 1.34806 406.269 51.1975C417.994 53.1093 429.602 55.6857 441.037 58.9143C395.293 30.0236 342.319 14.731 288.259 14.8104C128.606 15.3074 -0.432866 145.467 0.00208065 305.569C-0.305456 386.865 33.4917 464.544 93.1295 519.611C86.9002 509.263 81.2739 498.562 76.2789 487.561C33.3643 436.706 9.9081 372.19 10.1124 305.569Z" fill="url(#dewa-paint0)"/>
  <path fill-rule="evenodd" clip-rule="evenodd" d="M69.8974 238.657C118.591 122.275 232.474 46.8334 358.328 47.5861C440.528 47.8248 519.265 80.8113 577.205 139.284C635.145 197.757 667.538 276.923 667.255 359.355C667.207 485.567 591.257 599.289 474.895 647.381C358.533 695.473 224.735 668.439 136.024 578.911C47.3124 489.383 21.2034 355.04 69.8974 238.657ZM104.028 407.829C141.631 497.778 229.618 556.106 326.876 555.559C459.133 555.093 566.015 447.279 565.704 314.649C565.68 217.115 507.001 129.224 417.086 92.043C327.171 54.8619 223.771 75.7312 155.2 144.9C86.6292 214.068 66.4251 317.88 104.028 407.829Z" fill="url(#dewa-paint1)"/>
  <path d="M576.899 305.624C576.946 205.481 525.699 112.332 441.196 58.969C429.649 55.7469 417.928 53.1893 406.09 51.3086C435.534 65.1455 462.352 84.0148 485.344 107.072C503.231 125.269 518.608 145.785 531.065 168.074C592.302 277.791 573.598 414.923 485.232 504.12C433.183 556.683 362.369 586.243 288.502 586.243C214.634 586.243 143.82 556.683 91.7714 504.12C86.4915 498.881 81.6049 493.305 76.8306 487.616C81.8256 498.617 87.4519 509.318 93.6811 519.666C146.707 569.068 216.433 596.481 288.81 596.383C448.423 595.855 577.396 465.686 576.899 305.624V305.624Z" fill="url(#dewa-paint2)"/>
  <path d="M143.165 94.6795C196.528 40.7436 269.157 10.407 344.922 10.407C420.687 10.407 493.316 40.7436 546.679 94.6795C564.991 113.337 580.761 134.341 593.58 157.146C604.928 170.603 615.148 184.978 624.136 200.123C577.14 62.8162 437.859 -20.1202 295.147 4.22383C152.435 28.5679 48.3321 153.021 49.2512 298.188C49.2512 308.947 49.869 319.367 50.88 329.788C52.5544 311.927 55.7872 294.248 60.541 276.953C65.4526 208.24 94.7674 143.569 143.165 94.6795V94.6795Z" fill="url(#dewa-paint3)"/>
  <path d="M344.689 596.322C440.64 595.67 530.396 548.677 585.776 470.097C641.157 391.517 655.372 290.985 623.958 200.063C614.971 184.918 604.751 170.543 593.403 157.086C656.087 269.584 636.959 410.103 546.502 501.637C493.169 555.629 420.529 586.004 344.745 586.004C268.961 586.004 196.321 555.629 142.987 501.637C89.2914 447.618 59.2223 374.401 59.4088 298.128C59.4088 291.031 59.8019 283.934 60.3636 276.893C55.6097 294.188 52.377 311.867 50.7026 329.728C66.3003 480.906 193.131 595.92 344.689 596.322V596.322Z" fill="url(#dewa-paint4)"/>
  <defs>
    <linearGradient id="dewa-paint0" x1="502.056" y1="128.929" x2="202.813" y2="-63.2795" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEF6F5"/><stop offset="0.07" stop-color="#FDEFF0"/>
      <stop offset="0.17" stop-color="#FBDBE1"/><stop offset="0.29" stop-color="#F8BAC8"/>
      <stop offset="0.42" stop-color="#F38DA6"/><stop offset="0.57" stop-color="#ED537A"/>
      <stop offset="0.73" stop-color="#E50D46"/><stop offset="0.76" stop-color="#E4003C"/>
    </linearGradient>
    <linearGradient id="dewa-paint1" x1="46.3399" y1="339.767" x2="475.329" y2="780.141" gradientUnits="userSpaceOnUse">
      <stop stop-color="#F5F9ED"/><stop offset="0.24" stop-color="#98C449"/>
      <stop offset="0.33" stop-color="#91C04A"/><stop offset="0.47" stop-color="#7EB54C"/>
      <stop offset="0.63" stop-color="#5EA350"/><stop offset="0.82" stop-color="#338A56"/>
      <stop offset="1" stop-color="#006D5C"/>
    </linearGradient>
    <linearGradient id="dewa-paint2" x1="54.066" y1="-130.926" x2="54.066" y2="730.807" gradientUnits="userSpaceOnUse">
      <stop stop-color="white"/><stop offset="1" stop-color="#97C347"/>
    </linearGradient>
    <linearGradient id="dewa-paint3" x1="698.62" y1="252.618" x2="682.82" y2="-20.4573" gradientUnits="userSpaceOnUse">
      <stop stop-color="#EAF0FA"/><stop offset="0.15" stop-color="#E6EEF9"/>
      <stop offset="0.28" stop-color="#DCE8F6"/><stop offset="0.41" stop-color="#C9DEF1"/>
      <stop offset="0.53" stop-color="#B0D0EA"/><stop offset="0.65" stop-color="#8FBEE1"/>
      <stop offset="0.77" stop-color="#66A8D6"/><stop offset="0.89" stop-color="#378EC9"/>
      <stop offset="1" stop-color="#0070BA"/>
    </linearGradient>
    <linearGradient id="dewa-paint4" x1="175.762" y1="145.888" x2="175.762" y2="580.911" gradientUnits="userSpaceOnUse">
      <stop stop-color="white"/><stop offset="1" stop-color="#C7DC9A"/>
    </linearGradient>
  </defs>
</svg>
```

Treat this block as the **single source of truth** for the brand mark in every ADK skill guide. Copy it verbatim — do not redraw, recolour, simplify, or substitute.

### 16.2 Sizing & placement notes

- Default display size is **42 × 42 px** via the `.cover-org .logo` CSS rule. Bump to 46–48 px only if your skill name is short and the cover row looks visually under-weighted.
- The artwork's native canvas is 668 × 671 (very nearly square). Keep the `viewBox` as-is — do not crop or re-fit.
- Place the SVG inside `.cover-org` as the first child, immediately followed by the wordmark text "Dubai Electricity & Water Authority". The flexbox rule on `.cover-org` aligns them on the same baseline.
- The mark only appears on the cover page (page 1). Header chips on subsequent pages use the small 8–10 px `.ph .brand .dot` square in `--primary`, **not** the full ring.

---

## 17. Complete Standalone Starter (canonical viewer)

Copy this entire block into a new file named `<Skill Name> - User Manual.html`. It is a **complete working manual** with three pages (Cover · one content page · Sign-off), every component class defined, and the linked DEWA logo (URL placeholder — point it at your actual asset host). Add more `<section class="page">` blocks to grow the guide; add component CSS only as you need it (the snippets in §6 are additive).

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Skill Name — User Manual</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  /* ---- Tokens (§4) ---------------------------------------------------- */
  :root{
    --primary:#007560; --primary-variant:#004937;
    --primary-tint:#D9EAE7; --primary-tint-soft:#E5F1EF;
    --accent-blue:#0B7BC1; --accent-blue-tint:#DAEBF6;
    --accent-orange:#E26D5A; --accent-bronze:#A2511A;
    --error:#B00020; --error-tint:#F3D9DE; --warn-bg:#FCF5E7;
    --grey-100:#EFEFF1; --grey-150:#F2F3F3; --grey-200:#D7D7DF;
    --grey-300:#BDBDBD; --grey-600:#6F6F6F; --grey-700:#4D4D4D; --grey-900:#222222;
    --bg:#FFFFFF; --ink:#222222;
    --t-h1:28pt; --t-h2:17pt; --t-h3:12pt; --t-h4:10.5pt;
    --t-body:9.5pt; --t-small:8.5pt; --t-caption:8pt; --t-mono:8.2pt;
    --font:-apple-system,"SF Pro Display","SF Pro Text","Helvetica Neue",system-ui,sans-serif;
    --mono:"SF Mono",ui-monospace,Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0;background:#E9EAEC;color:var(--ink);
    font-family:var(--font);-webkit-font-smoothing:antialiased}
  body{padding:32px 0 48px}

  /* ---- Page geometry (§3) -------------------------------------------- */
  .page{width:210mm;height:297mm;background:#fff;margin:0 auto 16px;
    box-shadow:0 1px 2px rgba(0,0,0,.08),0 8px 28px rgba(0,0,0,.10);
    position:relative;overflow:hidden;page-break-after:always;
    color:var(--ink);font-size:var(--t-body);line-height:1.5}
  .page:last-child{page-break-after:auto}
  .ph{position:absolute;top:0;left:0;right:0;height:18mm;padding:8mm 16mm 0;
    display:flex;align-items:flex-end;justify-content:space-between;
    border-bottom:1px solid var(--grey-100)}
  .ph .brand{display:flex;align-items:center;gap:8px}
  .ph .brand .dot{width:10px;height:10px;border-radius:2px;background:var(--primary)}
  .ph .brand .t{font-size:var(--t-small);color:var(--grey-900);font-weight:600}
  .ph .meta{font-size:var(--t-caption);color:var(--grey-600)}
  .pf{position:absolute;left:0;right:0;bottom:0;height:14mm;padding:0 16mm;
    display:flex;align-items:center;justify-content:space-between;
    color:var(--grey-600);font-size:var(--t-caption);border-top:1px solid var(--grey-100)}
  .pf .pn b{color:var(--primary);font-weight:700;font-variant-numeric:tabular-nums}
  .pbody{position:absolute;top:18mm;left:16mm;right:16mm;bottom:14mm;padding-top:14mm}

  /* ---- Typography (§5) ----------------------------------------------- */
  h1.t{font-size:var(--t-h1);line-height:1.05;letter-spacing:-0.01em;
    margin:0;color:var(--grey-900);font-weight:700}
  h2.t{font-size:var(--t-h2);line-height:1.15;margin:0 0 5mm;
    color:var(--grey-900);font-weight:700;letter-spacing:-0.005em}
  h3.t{font-size:var(--t-h3);margin:0 0 3mm;font-weight:600;color:var(--grey-900)}
  .pbody h2.t:not(:first-child){margin-top:8mm}
  .pbody h3.t:not(:first-child){margin-top:6mm}
  p{margin:0 0 8px}
  .lede{color:var(--grey-900);font-size:11pt;line-height:1.55}
  .muted{color:var(--grey-600)}
  .eyebrow{font-size:var(--t-caption);letter-spacing:.18em;
    text-transform:uppercase;color:var(--primary);font-weight:600}

  /* ---- Cover (§6.A.2) ------------------------------------------------ */
  .cover{background:#fff}
  .cover .rail{position:absolute;left:0;top:0;bottom:0;width:18mm;background:var(--primary)}
  .cover .rail .badge{position:absolute;top:18mm;left:50%;transform:translateX(-50%);
    width:11mm;height:11mm;border-radius:50%;background:#fff;display:flex;
    align-items:center;justify-content:center;color:var(--primary);font-weight:800;font-size:10pt}
  .cover .rail .vt{position:absolute;bottom:14mm;left:50%;
    writing-mode:vertical-rl;transform:translateX(-50%) rotate(180deg);
    color:rgba(255,255,255,.85);font-size:8.5pt;letter-spacing:.3em;text-transform:uppercase}
  .cover-body{position:absolute;left:30mm;right:18mm;top:0;bottom:0;
    padding:22mm 0 18mm;display:flex;flex-direction:column}
  .cover-org{display:inline-flex;gap:14px;align-items:center;color:var(--grey-900);
    font-size:11pt;letter-spacing:.18em;text-transform:uppercase;font-weight:700;margin-bottom:8mm}
  .cover-org .logo{width:42px;height:42px;display:block}
  .cover h1{margin:8mm 0 4mm;font-size:48pt;line-height:1;letter-spacing:-0.02em;
    color:var(--grey-900);font-weight:700}
  .cover h1 .em{color:var(--primary);display:block}
  .cover-eyebrow{display:inline-flex;gap:10px;align-items:center;color:var(--grey-600);
    font-size:var(--t-small);letter-spacing:.22em;text-transform:uppercase;margin-top:2mm}
  .cover-eyebrow .pip{width:24px;height:1.5px;background:var(--primary);display:inline-block}
  .cover .sub{color:var(--grey-900);font-size:14pt;font-weight:500;max-width:140mm;margin-top:10mm}
  .cover .dept-chain{display:flex;flex-wrap:wrap;align-items:center;gap:10px;
    margin-top:10mm;padding:5mm 6mm;border:1px solid var(--grey-200);
    border-left:3px solid var(--primary);background:var(--grey-100);border-radius:6px;
    font-size:10pt;color:var(--grey-600);font-weight:500}
  .cover .dept-chain .sep{color:var(--grey-300);font-weight:400}
  .cover .dept-chain .dept.current{color:var(--primary);font-weight:700}
  .cover .pillars{margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
  .pillar{border:1px solid var(--grey-200);border-radius:10px;padding:14px 14px 16px;background:#fff}
  .pillar .pi{width:30px;height:30px;border-radius:8px;background:var(--primary-tint);
    color:var(--primary);display:flex;align-items:center;justify-content:center;margin-bottom:10px}
  .pillar h4{margin:0 0 4px;font-size:11pt;font-weight:700}
  .pillar p{margin:0;color:var(--grey-600);font-size:var(--t-small);line-height:1.45}
  .cover .meta-row{margin-top:8mm;padding-top:6mm;border-top:1px solid var(--grey-100);
    display:flex;justify-content:space-between;align-items:flex-end;gap:16px;
    color:var(--grey-600);font-size:var(--t-small)}
  .meta-row .vbig{color:var(--grey-900);font-weight:700;font-size:11pt;letter-spacing:.05em}
  .meta-row .stack{display:flex;flex-direction:column;gap:2px}

  /* ---- Tables, callouts, code (§6.B.1–B.3) --------------------------- */
  .tbl{width:100%;border-collapse:separate;border-spacing:0;font-size:var(--t-small)}
  .tbl thead th{background:var(--primary);color:#fff;text-align:left;padding:7px 10px;
    font-size:var(--t-caption);letter-spacing:.06em;text-transform:uppercase;font-weight:600}
  .tbl thead th:first-child{border-top-left-radius:8px}
  .tbl thead th:last-child{border-top-right-radius:8px}
  .tbl tbody td{padding:5.5px 10px;border-bottom:1px solid var(--grey-100);
    vertical-align:top;color:var(--grey-900)}
  .tbl tbody tr:nth-child(even) td{background:#FAFAFB}

  .callout{border-radius:10px;padding:12px 14px;display:grid;
    grid-template-columns:18px 1fr;gap:10px;align-items:flex-start;
    font-size:var(--t-small);line-height:1.5}
  .callout .ico{width:18px;height:18px;border-radius:50%;display:flex;
    align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:10pt}
  .callout.info{background:var(--accent-blue-tint);color:#0A4F7A}
  .callout.info .ico{background:var(--accent-blue)}
  .callout.success{background:var(--primary-tint-soft);color:var(--primary-variant)}
  .callout.success .ico{background:var(--primary)}
  .callout.warn{background:var(--warn-bg);color:#7B5A0F}
  .callout.warn .ico{background:#C28B14}
  .callout.danger{background:#FBE9EC;color:#7A0716}
  .callout.danger .ico{background:var(--error)}

  .code{background:#0F1A18;color:#E8F1EE;border-radius:10px;padding:11px 14px;
    font-family:var(--mono);font-size:var(--t-mono);line-height:1.45;
    white-space:pre-wrap;word-break:break-word;border:1px solid #08332A}

  /* ---- Print (§8) ---------------------------------------------------- */
  @media print{
    body{background:#fff;padding:0}
    .page{box-shadow:none;margin:0}
    *,*::before,*::after{
      -webkit-print-color-adjust:exact!important;
      print-color-adjust:exact!important;
      color-adjust:exact!important}
  }
</style>
</head>
<body>

<!-- ===== Page 1 — Cover ============================================== -->
<section class="page cover" data-screen-label="01 Cover">
  <div class="rail">
    <div class="badge">v1.0</div>
    <div class="vt">DEWA · ADK · &lt;Skill&gt;</div>
  </div>
  <div class="cover-body">
    <div class="cover-org">
      <!-- Paste the inline DEWA logo SVG from §16.1 here -->
      Dubai Electricity &amp; Water Authority
    </div>
    <h1>Skill Name<span class="em">User Manual</span></h1>
    <div class="cover-eyebrow"><span class="pip"></span>Agent Development Kit</div>
    <p class="sub">One-sentence description of what the skill does and who it's for.</p>
    <div class="dept-chain">
      <span class="dept">Innovation and the Future</span>
      <span class="sep">›</span>
      <span class="dept">Digital Solutions and Services</span>
      <span class="sep">›</span>
      <span class="dept current">Your Team</span>
    </div>
    <div class="pillars">
      <div class="pillar"><h4>Pillar one</h4><p>One-line value statement.</p></div>
      <div class="pillar"><h4>Pillar two</h4><p>One-line value statement.</p></div>
      <div class="pillar"><h4>Pillar three</h4><p>One-line value statement.</p></div>
    </div>
    <div class="meta-row">
      <div class="stack"><span>Document</span><span class="vbig">Version 1.0</span></div>
      <div class="stack"><span>Released</span><span class="vbig">Month YYYY</span></div>
      <div class="stack"><span>Classification</span><span class="vbig">Internal Use Only</span></div>
    </div>
  </div>
</section>

<!-- ===== Page 2 — Sample content page ================================ -->
<section class="page" data-screen-label="02 Overview">
  <header class="ph">
    <div class="brand"><span class="dot"></span><span class="t">Skill Name</span></div>
    <div class="meta">v1.0 · Month YYYY</div>
  </header>
  <div class="pbody">
    <h1 class="t">Overview</h1>
    <p class="lede muted">A short paragraph framing what this section covers.</p>

    <h2 class="t">What it does</h2>
    <p>Body copy explaining the core capability.</p>

    <table class="tbl">
      <thead><tr><th>Input</th><th>Type</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>config.yaml</td><td>file</td><td>Source of truth for runtime parameters.</td></tr>
        <tr><td>--target</td><td>flag</td><td>Optional override for the default target.</td></tr>
      </tbody>
    </table>

    <div class="callout info" style="margin-top:6mm">
      <div class="ico">i</div>
      <div>This skill assumes the agent host has network access to the configured endpoint.</div>
    </div>
  </div>
  <footer class="pf">
    <div class="cls">Internal Use Only</div>
    <div class="pn">Page <b>02</b> / 03</div>
  </footer>
</section>

<!-- ===== Page 3 — Sign-off =========================================== -->
<section class="page" data-screen-label="03 Sign-off">
  <header class="ph">
    <div class="brand"><span class="dot"></span><span class="t">Skill Name</span></div>
    <div class="meta">v1.0 · Month YYYY</div>
  </header>
  <div class="pbody">
    <h1 class="t">Document Sign-off</h1>
    <h2 class="t">Approvers</h2>
    <table class="tbl">
      <thead><tr><th>Name</th><th>Role</th><th>Date</th></tr></thead>
      <tbody>
        <tr><td>—</td><td>Skill Owner</td><td>YYYY-MM-DD</td></tr>
        <tr><td>—</td><td>Engineering Lead</td><td>YYYY-MM-DD</td></tr>
        <tr><td>—</td><td>Department Head</td><td>YYYY-MM-DD</td></tr>
      </tbody>
    </table>
    <h2 class="t">Revision History</h2>
    <table class="tbl">
      <thead><tr><th>Version</th><th>Date</th><th>Author</th><th>Summary</th></tr></thead>
      <tbody><tr><td>1.0</td><td>YYYY-MM-DD</td><td>—</td><td>Initial release.</td></tr></tbody>
    </table>
  </div>
  <footer class="pf">
    <div class="cls">Internal Use Only</div>
    <div class="pn">Page <b>03</b> / 03</div>
  </footer>
</section>

</body>
</html>
```

---

## 18. Complete Standalone Print Sibling

Save this as `<Skill Name> - User Manual-print.html`. It is identical to §17 except for the additional `@page` rule and the auto-print script. Opening it in a browser triggers the print dialog automatically — the user picks **Save as PDF**.

```html
<!-- ...same <head> + <style> + <body> as §17, with these two additions: -->

<!-- 1) Add @page rule INSIDE the <style> block, at the very top: -->
<style>
  @page { size: A4 portrait; margin: 0; }
  /* ... rest of CSS unchanged ... */
</style>

<!-- 2) Add this script just before </body>: -->
<script>
(async () => {
  try {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
  } catch (e) {}
  if (document.readyState !== 'complete') {
    await new Promise(r => window.addEventListener('load', r, { once: true }));
  }
  setTimeout(() => window.print(), 500);
})();
</script>
```

Both files (§17 and §18) render correctly out of the box — paste the inline DEWA logo SVG from §16.1 into the `.cover-org` slot in each, and you're done. No folders, no `assets/` directory, no network dependency.

---

*End of spec. This document, the inline logo (§16.1), the starter template (§17), and the print sibling (§18) together form the complete kit needed to produce a DEWA-branded ADK skill user manual.*
