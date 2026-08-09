# Pazhayannur Community Portal — working instructions

This is the community portal for Pazhayannur, a town in Thalappilly Taluk,
Thrissur District, Kerala. It is **not** the official Grama Panchayat website.

Stack: **Astro 7** (static output) · **Tailwind CSS v4** · **Alpine.js** ·
deployed to **Cloudflare Pages**.

---

## 1. The design system is called Panchavarnam. Do not deviate from it.

The palette derives from the five natural powders used in *kalamezhuthu*,
the ritual floor drawing of Kerala's temple courtyards. Every colour on this
site traces back to one of them.

| Token | Hex | Powder | Used for |
|---|---|---|---|
| `rice` | `#F4F0E4` | അരിപ്പൊടി | body text, hairlines |
| `turmeric` | `#E8A317` | മഞ്ഞൾ | primary accent, CTAs, links |
| `vaka` | `#2F7D5B` | വാകയില | geography section key |
| `kumkum` | `#C3341B` | ചുവപ്പ് | culture section key |
| `ink` | `#100E0C` | കരി | page background |

Supporting surfaces: `ink2` (`#191512`) for alternating bands, `ink3`
(`#241F1A`) for raised surfaces, `vakadeep` (`#14452F`) for gradients.

**Never use a Tailwind default colour.** No `bg-amber-500`, `text-slate-400`,
`border-gray-700`, `bg-emerald-600`. If a shade is needed, use an opacity
modifier on a system token: `text-rice/60`, `border-rice/12`, `bg-rice/[.04]`.

**Never introduce a new hex value** in a component. If a genuinely new colour
is needed, add it to `@theme` in `src/styles/global.css` first and justify it
against the five powders.

### Section colour keys
Each major section is keyed to one powder and shows a five-dot index:

1. History → rice
2. Administration → turmeric
3. Geography → vaka
4. Life & culture → kumkum
5. Development focus → charcoal (`ink3`)

Preserve this mapping. It is the structural signature of the design.

---

## 2. Tailwind v4 — there is no config file

Configuration lives in `@theme` inside `src/styles/global.css`.

- **Do not create `tailwind.config.js` or `tailwind.config.ts`.** It is a v3
  pattern and mixing it in causes errors.
- Do not install or configure `postcss` or `autoprefixer` — v4 includes them.
- Do not use `@tailwind base/components/utilities` directives. v4 uses a single
  `@import "tailwindcss";`.
- Do not use the deprecated `@astrojs/tailwind` integration. This project uses
  `@tailwindcss/vite`.
- `outline-none` is now `outline-hidden` in v4.

---

## 3. Typography

| Utility | Family | Use |
|---|---|---|
| `font-display` | Bricolage Grotesque | headings, numbers, card titles |
| `font-body` | Instrument Sans | paragraphs, UI (default) |
| `font-mono` | JetBrains Mono | coordinates, codes, labels, small caps |
| `font-mal` | Anek Malayalam | **all Malayalam text** |

Small labels use this exact recipe:
`font-mono text-[10px] tracking-[0.22em] uppercase text-rice/45`

Section headings use:
`font-display font-extrabold text-5xl md:text-7xl leading-[0.92] tracking-[-0.035em]`

---

## 4. Bilingual convention — this is not optional

Malayalam is a first-class language on this site, not a translation layer.

- Every heading, card title and label has an English line and a Malayalam line.
- English sits first at full weight; Malayalam sits beneath it, one step down
  in size and at lower opacity (`text-rice/40` to `/50`).
- **Always wrap Malayalam in `lang="ml"`** so screen readers pronounce it
  correctly and browsers pick the right font fallback:
  ```astro
  <h2 class="font-display font-extrabold text-5xl">
    Geography
    <span lang="ml" class="block font-mal text-2xl text-rice/45 mt-3">ഭൂമിശാസ്ത്രം</span>
  </h2>
  ```
- Malayalam strings live in the `ml` field of the JSON data files. Do not
  hardcode them into components.
- Do not machine-translate. If a Malayalam string is missing, leave the field
  empty and flag it rather than inventing one.

---

## 5. Astro rules

**Content must render server-side.** The original prototype used Alpine
`x-for` loops, which meant Google saw an empty page. Never reintroduce that.

- Lists render with `.map()` in the `.astro` component, from JSON in `src/data/`.
- Alpine is only for genuine interactivity: mobile menu, accordion open/close,
  ward selector, language toggle. Nothing that holds content.
- Never put page content inside `<template x-for>`.

Other conventions:

- Components are `.astro` unless there is a specific reason otherwise.
- Structured data (metrics, sectors, council) → `src/data/*.json`.
- Long-form prose (history articles, biographies) → `src/content/` as Markdown.
- Images → `src/assets/`, rendered through `astro:assets` `<Image>` so they get
  AVIF/WebP and correct sizing. Never hotlink Unsplash in production.
- Every page uses `src/layouts/Base.astro` and passes a real `title` and
  `description`.

---

## 6. Motion

- Reveal animations use the `.reveal` class plus `--d` for stagger delay:
  `style={\`--d:\${i * 110}ms\`}`. The IntersectionObserver lives in `Base.astro`.
- Easing is always `var(--ease-panchavarnam)`.
- **Every animation must respect `prefers-reduced-motion`.** Content must be
  fully readable with motion disabled.
- No new animation libraries. No GSAP, no Framer Motion, no AOS.

---

## 7. Accuracy and tone

This portal carries a real town's history. Accuracy matters more than polish.

- The Pazhayan etymology and the Kuttadanthodu account are **oral tradition**.
  Always phrase them as such ("local tradition holds", "accounts tell of").
  Never state them as documented fact.
- Do not invent dates, names, figures or statistics. If a value is unknown,
  leave the field empty or write `null` — never fill it with a plausible guess.
- Known open question: the figures list 22 wards, but the 2025 committee is
  recorded as 24 members. Do not silently reconcile these.

**This is a community portal, not a government site.** Never write copy that
implies it can deliver official services. No "Pay property tax", no "Apply for
certificate", no "Book an appointment". Guides that explain a procedure and
link out to the official LSGD portal are correct; anything that looks like a
transaction endpoint is not.

The footer disclaimer must stay on every page:
> This is a community-driven initiative celebrating the heritage and progress
> of Pazhayannur. For official government services, please contact the
> Panchayat office.

---

## 8. Accessibility floor

- Contrast: body text no lighter than `text-rice/60` on `ink` backgrounds.
- Every interactive element keeps a visible `:focus-visible` ring.
- Images need real `alt` text describing the subject, not the filename.
- Icon-only buttons need `aria-label`.
- Heading levels descend in order. One `<h1>` per page.
