# GitHub Pages Recipe Site — Design Spec

Static recipe website deployed via GitHub Pages, generated from existing YAML recipe files by extending `generate.py`.

## Prerequisites

This spec depends on the core recipe-engine being implemented first (at minimum: project scaffolding, recipe loader, and `generate.py` from `docs/superpowers/plans/2026-03-11-recipe-engine.md` Chunks 1-2). The GitHub Pages work extends `generate.py` — it cannot be built until that script exists.

## Breaking Changes from Core Spec

This spec intentionally changes two decisions from `docs/superpowers/specs/2026-03-11-recipe-engine-design.md`:

1. **Repo visibility:** Core spec says "Private". This spec changes it to **Public** because free GitHub Pages requires a public repo. The user explicitly approved this change during brainstorming.
2. **`docs/` directory layout:** Core spec puts markdown at `docs/<slug>.md` (flat). This spec moves markdown to `docs/recipes/<slug>.md` to coexist with HTML files. The existing `docs/spicy-chicken-tikka-masala.md` will be moved during implementation. The core spec should be updated to reflect this new layout.

## Overview

- **Homepage:** Grouped list of recipes by cuisine, with status/time/cost metadata
- **Detail pages:** Full recipe with checkable ingredients for cooking mode
- **Tech:** Python-generated static HTML/CSS, vanilla JS for ingredient checkboxes only
- **Hosting:** GitHub Pages serving from `docs/` directory
- **Repo visibility:** Public (required for free GitHub Pages)

## Site Structure

```
docs/
├── index.html              # Homepage — grouped recipe list
├── style.css               # Shared stylesheet (dark theme, mobile-first)
├── recipes/
│   ├── spicy-chicken-tikka-masala.html   # One detail page per recipe
│   └── ...
└── superpowers/            # Existing specs/plans (unchanged)
```

The `docs/` directory serves double duty: GitHub Pages root and existing spec/plan storage. Recipe HTML goes in `docs/recipes/` to avoid conflicts with the superpowers subdirectory.

## Homepage (`docs/index.html`)

### Layout
- Header: site title
- Recipes grouped by cuisine in a simple list
- Each row: recipe name (linked to detail page), status badge, prep+cook time, cost/serving
- Draft recipes shown in muted/dimmed text
- Mobile-first single column layout

### Grouping
- Primary grouping: by cuisine
- Recipes without a cuisine go under "Other"
- Within each group, sort by status (staple → tested → draft), then alphabetically

## Recipe Detail Pages (`docs/recipes/<slug>.html`)

### Layout
- Back link to index
- Recipe name as heading
- Metadata badges: status, cuisine, category, tags, time, cost, servings, equipment
- Checkable ingredients list (tap to strike through)
- Numbered steps
- Storage section (fridge days, freezer days, reheating instructions)
- Notes section

### Checkable Ingredients
- Each ingredient rendered as a checkbox + label
- Label text constructed from YAML fields: `{qty} {unit} {item}` (e.g., "800 g chicken breast"). If `qty` or `unit` is missing, omit gracefully.
- Tapping/clicking toggles strikethrough styling
- State is not persisted — resets on page refresh
- Implemented with ~10 lines of vanilla JS (inline or single `script.js` file)

### Slug derivation
- HTML page slugs come from the YAML filename stem (same as core spec): `spicy-chicken-tikka-masala.yaml` → `docs/recipes/spicy-chicken-tikka-masala.html`

## Styling

- Dark theme (dark background, light text, accent color for headings/badges)
- Mobile-first responsive design — must be comfortable to use on a phone while cooking
- Single `style.css` shared across all pages
- Status badges: colored by status (staple = green, tested = orange, draft = gray)
- Clean typography, generous line spacing for readability

## Generation

### Changes to `generate.py`

Extend the existing script to output HTML in addition to markdown:

1. **HTML templates** — use `jinja2` for cleaner template rendering (add to `requirements.txt`). Jinja2 is added because building multi-page HTML with Python string formatting is error-prone and hard to maintain — Jinja2 is lightweight and purpose-built for this.
2. **Output HTML to `docs/`:**
   - `docs/index.html` — homepage
   - `docs/recipes/<slug>.html` — detail pages
   - `docs/style.css` — stylesheet (written from a template or static file)
3. **Continue generating markdown** — existing `docs/<slug>.md` files move to `docs/recipes/<slug>.md` to coexist with HTML

### Template files

Store Jinja2 templates in `scripts/templates/`:
```
scripts/templates/
├── index.html        # Homepage Jinja2 template
├── recipe.html       # Recipe detail Jinja2 template
```

Store static assets in `scripts/static/`:
```
scripts/static/
├── style.css         # Stylesheet (copied to docs/ as-is, not a template)
```

### Generation flow

```
YAML recipes + equipment.yaml
        ↓
    generate.py
        ↓
    ┌───────────────────────────┐
    │ docs/index.html           │
    │ docs/recipes/<slug>.html  │
    │ docs/recipes/<slug>.md    │
    │ docs/style.css            │
    │ README.md                 │
    └───────────────────────────┘
```

## Dependencies

Add to `requirements.txt`:
```
pyyaml
jinja2
```

### README.md updates

The generated `README.md` continues to link to markdown files (now at `docs/recipes/<slug>.md`). It also adds a link at the top to the live GitHub Pages site.

### Required static files

- `docs/.nojekyll` — empty file to disable Jekyll processing on GitHub Pages (prevents interference with static HTML)
- `docs/index.html` must include `<meta name="viewport" content="width=device-width, initial-scale=1">` for mobile rendering

## Deployment

1. Make repo public: `gh repo edit --visibility public`
2. Enable GitHub Pages: Settings → Pages → Source: `Deploy from a branch` → Branch: `main`, folder: `/docs`
3. Site will be available at `https://yashashav-dk.github.io/recipe-engine/`

## Workflow

1. Add/edit a YAML recipe in `recipes/`
2. Run `python scripts/generate.py`
3. Commit YAML + generated HTML
4. Push — site updates automatically

## Out of Scope

- Search functionality (filter links are sufficient for <20 recipes)
- JavaScript frameworks (React, Vue, etc.)
- Build tools (webpack, vite, etc.)
- CI/CD auto-generation (run generate.py manually for now)
- Persistent ingredient checkbox state (resets on refresh)
- Custom domain
- Custom 404 page (rely on GitHub's default)
