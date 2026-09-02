# ADAMA BrandWell Design System

**Version:** 2.0
**Company:** ADAMA — crop protection solutions (herbicides, fungicides, insecticides)
**Sources:** ADAMA BrandWell, the official global brand portal (adama.frontify.com) — full sweep
of Brand Basics, Listen > Learn > Deliver, Guidelines, Assets/Templates, Media Library and
Global Campaigns, August 2026. Plus the official ADAMA asset library (logos, 'A' shapes,
tab and container shapes, brand promise templates, LL Brown and Aleo font files).

---

## What's in this Design System

| Path | Contents |
|---|---|
| `styles.css` | Global entry point — `@import` this one file |
| `tokens/colors.css` | Full palette + **colour line aliases** (primary / supporting / contrast) + CMYK & Pantone reference |
| `tokens/typography.css` | Self-hosted LL Brown and Aleo `@font-face`, sizes, weights, line-heights |
| `tokens/spacing.css` | Spacing scale, radii, shadows, z-index, transitions |
| `tokens/patterns.css` | Product pattern tiles + `.adama-pattern--*` helper classes |
| `tokens/base.css` | Minimal reset + base element styles |
| `rules/` | **The hard brand rules, taken from BrandWell. Read these before designing.** |
| `assets/logos/` | RGB, Black, White — Horizontal and Vertical |
| `assets/brand-promise/` | Full Speech Bubble graphics (5 lines × primary/secondary) + stacked wordmarks |
| `assets/shapes-a/` | Official 'A' shape cut-outs (transparent PNG) — 4 crops × 5 colourways × horizontal/vertical, **plus `a-shape-full.svg`** (the whole 'A' as vector — the four crops are windows on it, verified IoU 0.995–1.000) and `logo-holder-white.png` (the white corner plate that holds the logo on ADAMA pieces) |
| `assets/reference/` | BrandWell's own figures — the crop diagram, Scale / Layout / Rotation and the three errors, captured from the portal |
| `assets/backgrounds/` | Seven ready-made 16:9 'A'-shape plates (Earth + Corporate families) — **not photography** |
| `assets/shapes/` | Tab and container shapes in all colourways |
| `assets/icons/brand/` | 11 core brand icons — ADAMA Green, Earth, White |
| `assets/icons/product/` | 4 sector icons — primary, secondary, green, earth, white |
| `assets/product-logos/` | ADAMA product logos, one folder per product |
| `assets/patterns/` | Product patterns — seamless tiles, flat swatches, primary treatment, .pat |
| `assets/misc/` | Recurring graphic elements (inseto de canto, texto legal) |
| `assets/fonts/` | LL Brown (8 OTF) and Aleo (2 variable TTF) |
| `components/core/` | Button, Badge, Tag, Card, ProductIcon React components |
| `guidelines/` | Specimen cards (colours, type, spacing, brand, voice, photography, naming) |
| `templates/` | Product sheet template |

### The `rules/` folder

| File | Covers |
|---|---|
| `brand-core.md` | Purpose, positioning, Backbone, values, behaviours, the official narrative |
| `color-usage.md` | **The line rule** — primary + supporting + contrast, tints, print values |
| `typography-and-casing.md` | The three typefaces, licensing, Title Case vs sentence case |
| `logo.md` | Versions, colours, clear space, minimum sizes, what to avoid, endorsements |
| `brand-promise.md` | The four options and their hierarchy, colour rule, lockups, translation |
| `shapes-and-icons.md` | 'A' shape, tab, container, lines, icons, circle graphic, product patterns |
| `backgrounds-and-a-shape.md` | **Como montar o fundo** — o que o manual literalmente autoriza, os 4 recortes, o pareamento de cor (o escuro atrás), tom sobre tom, a anatomia do anúncio impresso e da peça social brasileira, camadas, números e CSS |
| `photography.md` | The four categories and their attributes; sourcing; AI-generation guidance |
| `voice-and-copy.md` | Tone, style, casing, key messaging themes, the LLD structure |
| `product-naming.md` | Naming rules, the request process, family descriptors, co-packs |
| `non-product-initiatives.md` | Internal vs external initiatives, key visuals, taglines |
| `adama-brasil-portfolio.md` | **The Brazilian portfolio** — every product, its category and its colour line |
| `governance.md` | What needs approval and from whom; font licensing; BrandWell map |
| `checklist.md` | Pre-delivery checklist |

---

## Company & product context

ADAMA is a major crop-protection company (subsidiary of ADAMA Ltd.) selling to Brazilian
farmers and agribusiness. The portfolio is organised into four product sectors, each with a
dedicated primary brand colour:

| Sector | Colour | Hex | Pantone |
|---|---|---|---|
| Crop Enhancement | Orange | `#f89e18` | 1375 C |
| Weed Control | Green | `#7db41e` | 368 C |
| Disease Control | Blue | `#00a0df` | 299 C |
| Pest Control | Purple | `#9d1d96` | 254 C |

Corporate identity uses ADAMA Green (`#009845`) and ADAMA Earth (`#978b87`) for all non-product
brand contexts.

**Brand pronunciation for voiceover and TTS: "Adamá"** — stress on the final syllable
(/adaˈma/). Never "ÁDama".

---

## Content fundamentals

**Purpose:** creating simplicity in agriculture.

**Brand promise:** Listen > Learn > Deliver — always Title Case with `>` dividers when used as a
phrase; lowercase when the actions are described separately ("we listen and learn from farmers so
we can deliver solutions they need").

**Tone:** informal, as if speaking with a friend. Serious, excited or slightly humorous depending
on the subject — **never sarcastic**. Technical content: clear and authoritative, **never
patronising or preaching**.

**Voice — the official rule:** use **we / our**, not they / your. Active voice. Short, clear
sentences. Tell stories and make it personal instead of listing facts and figures. Use
testimonials and direct quotes. Sound conversational, not academic or institutional. Avoid
industry jargon.

> ⚠ Version 1.0 of this design system said "use *you* more than *we*". That was the opposite of
> the official BrandWell guideline and has been corrected.

**Casing:**
- Headlines: Title Case or sentence case — never ALL CAPS for headlines
- Product names and product category names: Title Case always
- ADAMA: always full caps
- "Listen > Learn > Deliver": always Title Case with arrows

**Emoji:** not used.

**Brazilian Portuguese:** all consumer-facing material should support or default to pt-BR.
English is used internally and for corporate material.

**Numbers:** metric. Hectares (ha), kilograms (kg), litres (L).

---

## Visual foundations

### Colours

Five tiers: Corporate (green + earth), Primary/Product (4), Secondary (paired accents), Utility
(grey/white/black) — **plus a contrast slot per line**. Every combination is a *line* with three
positions: primary, supporting secondary, contrast. **Never mix lines.**

Any tint of ADAMA Earth is permitted; tints of Primary, Secondary or Utility are not.
Full table, CMYK and Pantone values: `rules/color-usage.md` and the comment block in
`tokens/colors.css`.

### Typography

- **Primary:** LL Brown (Lineto) — rounded, geometric humanist sans. **Self-hosted OTFs in
  `assets/fonts/`, wired up in `tokens/typography.css`. No substitution — do not fall back to
  Figtree or any other Google Font.**
- **Secondary:** Aleo — slab serif, technical tone. Short accents only: subheadings, intro text,
  pull quotes.
- **Alternate:** Arial — only for MS Office output.

External agencies must purchase their own LL Brown licence from **Lineto** (one licence = one
company, five users).

### Shapes & motifs

Derived from the 'A' in the logo. All follow the angle of the ADAMA 'A' and come in all product
colourways. Never alter, stretch or skew them.

- **'A' Shape** — dynamic background shapes. **Holds images.** Max two cropped instances per
  composition; at most one exterior point of the same shape visible; may be rotated.
- **Tab Shape** — section headers, labels, step indicators. Single-sided when side-aligned,
  double-sided when centred, always anchored to a page edge.
- **Container Shape** — pull quotes, call-outs, tips. **Holds text, never images.**
  Ideally one per design.
- **Lines** — dotted (personality) + solid (structure). Brand colours only, **never black**;
  a dotted line never outlines text.

### Backgrounds

- Primary: white (`#ffffff`)
- Secondary surface: Earth 10% (`#f4f2f2`)
- Product sections: full-bleed solid product colour, optionally with a Tab or Container shape
- No gradients on brand elements. The only exceptions: tints of Earth, and the product patterns'
  "primary treatment" (an understated gradient over the matching primary colour).

### Corner radii

Consistently soft and rounded — ADAMA avoids sharp corners. Buttons are always pills
(`border-radius: 9999px`). Cards use `16px`. Never `0` radius on interactive elements.

### Shadows

Warm earth-toned shadows (not cold blue-grey). Five levels from `xs` to `xl`. Use sparingly —
primarily on cards and modals.

### Animation

No brand-defined animation spec. Recommended defaults: 150–200 ms `ease` for micro-interactions,
300 ms `ease` for state or panel transitions. No bouncy/spring animation on professional
collateral.

### Hover states

Buttons darken (primary → secondary/dark variant). Cards lift with `translateY(-2px)` + shadow
increase. Links go from Corporate Green to Secondary Corporate Green.

### Iconography

Thin-stroke line icons (1.5–2 px). Consistent stroke weight, rounded corners and tips, simple
shapes. Never heavily filled, never sharp-cornered, never overly detailed. Four families: Core
Icons (15 brand icons), Purchased Icons, Crop Icons, Product/Sector Icons. Sector icons must
always carry a text qualifier ("Herbicida"). CDN substitute for prototyping: **Lucide Icons**.

### Layout

Lots of white. Background is either a flat line colour or a photo, with one or two cropped 'A'
shapes creating movement; a photo may sit inside an 'A' shape. Typical print-ad hierarchy: logo
at the top · product name (Title Case, large) · campaign headline · product or crop image in
motion · body copy with CTA at the foot · Brand Promise Graphic bleeding off the top of the
sides.

---

## Logo usage rules

1. Always icon + wordmark together (vertical preferred; horizontal when space-constrained).
   If impossible, **wordmark alone** — never the icon alone.
2. Never recolour — only the approved versions (two colour, black, white).
3. Never stretch, skew or alter proportions.
4. Never use the 'A' icon to replace the letter A in text.
5. Clear space on all sides = the height of the 'A' icon.
6. Minimum sizes: icon 4 mm / 50 px · wordmark 10 mm / 75 px · with endorsement 17 mm / 100 px.
7. Never apply a product pattern border around the 'A' — that treatment was revoked.
8. Endorsement lockups require Global Brand team approval for every use.

---

## Components

Located in `components/core/`:
- **Button** — pill-shaped, variants (primary/outline/ghost/secondary), 3 sizes, all brand colours
- **Badge** — small status/category label, product + semantic variants
- **Tag** — product-category chips with optional dismiss
- **Card** — surface container, 4 variants + product colour tints
- **ProductIcon** — circular product-category symbol

```html
<link rel="stylesheet" href="./_ds/adama-brandwell/styles.css">
<script src="./_ds/adama-brandwell/_ds_bundle.js"></script>
```
```js
const { Button, Badge, Tag, Card } = window.ADAMADesignSystem;
```

---

## Governance — what needs approval

Translation of Listen > Learn > Deliver (Global Brand Manager) · endorsement lockups (Global
Brand team, every use) · new product names (Global PSM + Trademark Counsel + Global Brand team) ·
label icons (Global PSM) · Formulation Technology names (Global Marketing) · special logo
applications (Global Marketing) · BrandWell access for external agencies (Global Brand Team).
Full table in `rules/governance.md`.

---

## ⚠ Caveats

- **Fonts integrated.** LL Brown (Lineto) and Aleo are self-hosted in `assets/fonts/`. No
  external font dependencies, no substitution.
- **Brand Promise complete.** All four options ship in `assets/brand-promise/`: Full Speech
  Bubble and Footer Graphic as A4 renders (5 lines + Earth, primary and secondary variants),
  Single Line wordmark in 7 colourways, and the Stacked wordmark. Editable AI / EPS / PDF
  sources (CMYK, RGB, PMS) live in the ADAMA asset drive.
- **Patterns complete.** The four product patterns are in `assets/patterns/` as seamless tiles
  (for `background-repeat`), flat swatches, primary-treatment artwork, and a Photoshop `.pat`.
- **Icons integrated as PNG.** The 11 core brand icons and the 4 sector icons are in
  `assets/icons/` in the approved colourways. The vector (EPS) originals live in the ADAMA asset
  drive; the purchased library and the crop-icon library are still only on BrandWell.
- **Brand shapes.** 'A' shape (40 official PNGs), Tab Shape and Container Shape are integrated in
  all colourways. Logos are cut-out (transparent) in colour, black and reversed white.
- **Product logos integrated.** 13 ADAMA products in `assets/product-logos/`, with the
  category and colour line of each documented in `rules/adama-brasil-portfolio.md`.
  Four still need their category confirmed: Expert Grow, Primer, TOV and the Biossoluções line.
- **Motion assets not included.** The After Effects projects (ADAMA Global Video Bumpers,
  lower thirds, vinhetas per product) and the rendered PNG sequences live in the ADAMA
  video drive, not here — they are too heavy for a design system.
- **BrownPro not used.** An older Brown cut (BrownPro, with Reclin and Alt variants) exists in
  the asset drive. The current official face is **LL Brown (BrownLL)**, already integrated.
  Do not mix the two.
