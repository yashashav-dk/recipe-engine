# Recipe Engine — Design Spec

Personal batch cooking recipe repository for an MS SE student at SJSU. A living recipe notebook meant for brainstorming, iterating, and building a repertoire over time.

## Core Philosophy

- **Living notebook first** — recipes start as rough ideas and get refined through cooking
- **Low friction** — adding a new recipe should be fast; most fields are optional
- **Metric units only** — grams/kilograms for weight, ml/litres for volume (250ml measuring cup as primary reference)
- **Git as history** — recipe evolution tracked naturally through commits

## Repository Structure

```
recipe-engine/
├── equipment.yaml              # Appliances & containers
├── recipes/
│   └── *.yaml                  # One YAML file per recipe
├── docs/
│   └── *.md                    # Auto-generated markdown per recipe
├── scripts/
│   ├── generate.py             # YAML → markdown + README index
│   └── meal_planner.py         # Weekly meal plan CLI
├── requirements.txt            # pyyaml
├── README.md                   # Auto-generated index & filtered views
└── .gitignore
```

## Recipe Schema

Each recipe is a YAML file in `recipes/`. Only `name` is required; everything else is optional so you can jot down ideas quickly and fill in details later.

```yaml
name: Chicken Tikka                     # REQUIRED
status: draft | tested | staple         # default: draft
cuisine: Indian
category: protein
servings: 8
prep_time_mins: 15
cook_time_mins: 25
equipment:
  - instant-pot
storage:
  fridge_days: 5
  freezer_days: 30
  reheating: "Microwave 2-3 mins or air-fry at 375°F for 5 mins"
cost_per_serving_usd: 1.50
tags:
  - high-protein
  - meal-prep
  - gluten-free
ingredients:
  - item: chicken thighs
    qty: 900
    unit: g
  - item: yogurt
    qty: 250
    unit: ml
steps:
  - Marinate chicken in yogurt and spices for 30 mins
  - Set Instant Pot to sauté mode...
notes: "Scales well to 2x. Use pot-in-pot method to cook rice simultaneously. Next time try adding kasuri methi."
```

### Allowed units

- Weight: `g`, `kg`
- Volume: `ml`, `L`
- Count: `piece`, `clove`, `sprig`, `bunch` (for items that don't weigh/measure well)

### Status field

- `draft` — idea or untested recipe (default)
- `tested` — cooked at least once, recipe works
- `staple` — reliable go-to, part of regular rotation

## Equipment File

`equipment.yaml` at repo root:

```yaml
appliances:
  - id: instant-pot
    name: Instant Pot Duo
    size: 6 quart
    notes: "Supports pot-in-pot method with inner pots"
  - id: air-fryer
    name: Gourmia Air Fryer
    size: medium
  - id: blender
    name: Vitamix E Series

containers:
  - id: glass-2l
    name: 2L Glass Batch Container
    count: 2
    capacity_liters: 2

measuring:
  - id: measuring-cup-250ml
    name: 250ml Measuring Cup
```

Recipes reference appliances by `id`. The generate script cross-references to warn about unknown equipment IDs.

## Scripts

### `scripts/generate.py`

Reads all YAML files in `recipes/` and produces:

1. **One markdown file per recipe** in `docs/` — human-readable version with all fields formatted nicely
2. **`README.md`** at repo root with:
   - Index table: name, cuisine, status, time, cost, tags
   - Grouped views: by cuisine, by equipment, by tag, by status
   - Per-appliance filtered sections (e.g., "Instant Pot recipes")
3. **Warnings** for:
   - Recipes referencing equipment not in `equipment.yaml`
   - Recipes missing key fields (non-blocking, just informational)

### `scripts/meal_planner.py`

CLI tool that generates a weekly batch cooking plan.

**Filters:**
- `--equipment` — only recipes using specified gear
- `--tags` — filter by tags (e.g., `high-protein`)
- `--max-budget-per-week` — budget cap in USD
- `--servings-per-day` — target servings needed per day
- `--status` — only include `tested` or `staple` recipes (default: exclude `draft`)

**Output:**
- Shopping list — combined ingredients across selected recipes, in metric, deduped
- Cook schedule — what to cook, prep order, estimated time
- Storage plan — fridge vs freezer allocation, eat-by dates

**Example:**
```bash
python scripts/meal_planner.py --tags high-protein --max-budget-per-week 40
```

### Dependencies

`requirements.txt`:
```
pyyaml
```

No heavy frameworks. Standard library for everything else (argparse, pathlib, etc).

## Repo Settings

- **Visibility:** Private
- **Platform:** GitHub, created via `gh repo create`

## Out of Scope (for now)

- Web UI / frontend
- Database (SQLite or otherwise)
- Nutrition info API integration
- CI/CD (GitHub Actions) — can add later when the recipe collection grows
- Strict schema validation — the repo is a notebook, not a production system
