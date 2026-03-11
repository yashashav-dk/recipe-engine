# Recipe Engine Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal batch cooking recipe repo with YAML recipes, auto-generated markdown, and a meal planner CLI.

**Architecture:** Flat YAML files in `recipes/` are the source of truth. Two Python scripts (`generate.py` and `meal_planner.py`) read the YAML and produce markdown documentation and weekly meal plans respectively. Only dependency is `pyyaml`.

**Tech Stack:** Python 3.8+, PyYAML, argparse, pathlib

**Spec:** `docs/superpowers/specs/2026-03-11-recipe-engine-design.md`

---

## Chunk 1: Project Scaffolding and Recipe Loading

### Task 1: Project scaffolding

**Files:**
- Create: `equipment.yaml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `recipes/` (directory)
- Create: `docs/` (directory)
- Create: `scripts/` (directory)
- Create: `tests/` (directory)

- [ ] **Step 1: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.DS_Store
```

- [ ] **Step 2: Create `requirements.txt`**

```
pyyaml
```

- [ ] **Step 3: Create `equipment.yaml`**

```yaml
appliances:
  - id: instant-pot
    name: Instant Pot Duo
    size: 5.7L
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

- [ ] **Step 4: Create empty directories with `.gitkeep`**

```bash
mkdir -p recipes docs scripts tests
touch recipes/.gitkeep docs/.gitkeep scripts/.gitkeep tests/.gitkeep
```

- [ ] **Step 5: Create a sample recipe for testing**

Create `recipes/chicken-tikka.yaml`:

```yaml
name: Chicken Tikka
status: tested
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
  reheating: "Microwave 2-3 mins or air-fry at 190°C for 5 mins"
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
  - item: ginger garlic paste
    qty: 30
    unit: g
  - item: red chilli powder
    qty: 10
    unit: g
  - item: turmeric
    qty: 5
    unit: g
  - item: garam masala
    qty: 10
    unit: g
  - item: salt
    qty: 10
    unit: g
  - item: oil
    qty: 30
    unit: ml
steps:
  - Marinate chicken thighs with yogurt, ginger garlic paste, red chilli powder, turmeric, garam masala, and salt for at least 30 mins
  - Set Instant Pot to sauté mode, add oil
  - Sear chicken pieces in batches until browned on both sides
  - Add 50ml water, close lid, set to pressure cook high for 8 mins
  - Natural release for 5 mins, then quick release
  - Optional - air-fry pieces at 200°C for 5 mins for extra char
notes: "Scales well to 2x. Use pot-in-pot method to cook rice simultaneously. Next time try adding kasuri methi."
```

- [ ] **Step 6: Create a minimal draft recipe for testing optional field handling**

Create `recipes/dal-tadka.yaml`:

```yaml
name: Dal Tadka
status: draft
cuisine: Indian
tags:
  - vegetarian
  - high-protein
ingredients:
  - item: toor dal
    qty: 500
    unit: g
  - item: onion
    qty: 2
    unit: piece
notes: "Need to figure out exact instant pot timing"
```

- [ ] **Step 7: Commit**

```bash
git add .gitignore requirements.txt equipment.yaml recipes/ docs/ scripts/ tests/
git commit -m "feat: project scaffolding with equipment and sample recipes"
```

---

### Task 2: Recipe loader module

**Files:**
- Create: `scripts/loader.py`
- Create: `tests/test_loader.py`

The loader is a shared module used by both `generate.py` and `meal_planner.py`. It reads YAML files and returns structured data.

- [ ] **Step 1: Write failing test for loading a single recipe**

Create `tests/test_loader.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from loader import load_recipe


def test_load_recipe_full(tmp_path):
    recipe_file = tmp_path / "chicken-tikka.yaml"
    recipe_file.write_text(
        "name: Chicken Tikka\n"
        "status: tested\n"
        "cuisine: Indian\n"
        "category: protein\n"
        "servings: 8\n"
        "prep_time_mins: 15\n"
        "cook_time_mins: 25\n"
        "equipment:\n"
        "  - instant-pot\n"
        "cost_per_serving_usd: 1.50\n"
        "tags:\n"
        "  - high-protein\n"
        "ingredients:\n"
        "  - item: chicken thighs\n"
        "    qty: 900\n"
        "    unit: g\n"
    )
    recipe = load_recipe(recipe_file)
    assert recipe["name"] == "Chicken Tikka"
    assert recipe["status"] == "tested"
    assert recipe["servings"] == 8
    assert recipe["equipment"] == ["instant-pot"]
    assert recipe["ingredients"][0]["item"] == "chicken thighs"
    assert recipe["slug"] == "chicken-tikka"


def test_load_recipe_minimal(tmp_path):
    recipe_file = tmp_path / "quick-idea.yaml"
    recipe_file.write_text("name: Quick Idea\n")
    recipe = load_recipe(recipe_file)
    assert recipe["name"] == "Quick Idea"
    assert recipe["status"] == "draft"
    assert recipe["servings"] is None
    assert recipe["equipment"] == []
    assert recipe["ingredients"] == []
    assert recipe["tags"] == []
    assert recipe["slug"] == "quick-idea"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/yashashav/jurisprudence/recipe-engine
python -m pytest tests/test_loader.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'loader'`

- [ ] **Step 3: Write loader implementation**

Create `scripts/loader.py`:

```python
"""Loads recipe and equipment YAML files into structured dicts."""

from pathlib import Path
from typing import Any

import yaml


def load_recipe(path: Path) -> dict[str, Any]:
    """Load a single recipe YAML file. Returns dict with defaults for missing fields."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    slug = path.stem  # kebab-case filename without extension

    return {
        "name": data["name"],
        "slug": slug,
        "status": data.get("status", "draft"),
        "cuisine": data.get("cuisine"),
        "category": data.get("category"),
        "servings": data.get("servings"),
        "prep_time_mins": data.get("prep_time_mins"),
        "cook_time_mins": data.get("cook_time_mins"),
        "equipment": data.get("equipment", []),
        "storage": data.get("storage"),
        "cost_per_serving_usd": data.get("cost_per_serving_usd"),
        "tags": data.get("tags", []),
        "ingredients": data.get("ingredients", []),
        "steps": data.get("steps", []),
        "notes": data.get("notes"),
    }


def load_all_recipes(recipes_dir: Path) -> list[dict[str, Any]]:
    """Load all .yaml files from the recipes directory."""
    recipes = []
    for path in sorted(recipes_dir.glob("*.yaml")):
        recipes.append(load_recipe(path))
    return recipes


def load_equipment(path: Path) -> dict[str, Any]:
    """Load equipment.yaml. Returns dict with all equipment IDs for cross-referencing."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    all_ids = set()
    equipment_by_id = {}
    for category in ("appliances", "containers", "measuring"):
        for item in data.get(category, []):
            all_ids.add(item["id"])
            equipment_by_id[item["id"]] = item

    return {
        "raw": data,
        "all_ids": all_ids,
        "by_id": equipment_by_id,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_loader.py -v
```

Expected: 2 passed

- [ ] **Step 5: Write tests for load_all_recipes and load_equipment**

Add to `tests/test_loader.py`:

```python
from loader import load_all_recipes, load_equipment


def test_load_all_recipes(tmp_path):
    (tmp_path / "aaa.yaml").write_text("name: AAA\n")
    (tmp_path / "bbb.yaml").write_text("name: BBB\nstatus: staple\n")
    (tmp_path / "not-yaml.txt").write_text("ignored")
    recipes = load_all_recipes(tmp_path)
    assert len(recipes) == 2
    assert recipes[0]["name"] == "AAA"
    assert recipes[1]["name"] == "BBB"


def test_load_equipment(tmp_path):
    equip_file = tmp_path / "equipment.yaml"
    equip_file.write_text(
        "appliances:\n"
        "  - id: instant-pot\n"
        "    name: Instant Pot Duo\n"
        "    size: 5.7L\n"
        "containers:\n"
        "  - id: glass-2l\n"
        "    name: 2L Glass Container\n"
        "    count: 2\n"
        "    capacity_liters: 2\n"
        "measuring:\n"
        "  - id: cup-250ml\n"
        "    name: 250ml Cup\n"
    )
    equip = load_equipment(equip_file)
    assert "instant-pot" in equip["all_ids"]
    assert "glass-2l" in equip["all_ids"]
    assert "cup-250ml" in equip["all_ids"]
    assert equip["by_id"]["instant-pot"]["name"] == "Instant Pot Duo"
```

- [ ] **Step 6: Run all loader tests**

```bash
python -m pytest tests/test_loader.py -v
```

Expected: 4 passed

- [ ] **Step 7: Commit**

```bash
git add scripts/loader.py tests/test_loader.py
git commit -m "feat: recipe and equipment YAML loader with tests"
```

---

## Chunk 2: Markdown Generator (`generate.py`)

### Task 3: Recipe markdown generation

**Files:**
- Create: `scripts/generate.py`
- Create: `tests/test_generate.py`

- [ ] **Step 1: Write failing test for single recipe markdown**

Create `tests/test_generate.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate import recipe_to_markdown


def test_recipe_to_markdown_full():
    recipe = {
        "name": "Chicken Tikka",
        "slug": "chicken-tikka",
        "status": "tested",
        "cuisine": "Indian",
        "category": "protein",
        "servings": 8,
        "prep_time_mins": 15,
        "cook_time_mins": 25,
        "equipment": ["instant-pot"],
        "storage": {
            "fridge_days": 5,
            "freezer_days": 30,
            "reheating": "Microwave 2-3 mins",
        },
        "cost_per_serving_usd": 1.50,
        "tags": ["high-protein", "meal-prep"],
        "ingredients": [
            {"item": "chicken thighs", "qty": 900, "unit": "g"},
            {"item": "yogurt", "qty": 250, "unit": "ml"},
        ],
        "steps": [
            "Marinate chicken for 30 mins",
            "Pressure cook 8 mins",
        ],
        "notes": "Scales well to 2x.",
    }
    md = recipe_to_markdown(recipe)
    assert "# Chicken Tikka" in md
    assert "**Status:** tested" in md
    assert "**Cuisine:** Indian" in md
    assert "**Servings:** 8" in md
    assert "900 g chicken thighs" in md
    assert "1. Marinate chicken for 30 mins" in md
    assert "Scales well to 2x." in md
    assert "**Fridge:** 5 days" in md


def test_recipe_to_markdown_minimal():
    recipe = {
        "name": "Quick Idea",
        "slug": "quick-idea",
        "status": "draft",
        "cuisine": None,
        "category": None,
        "servings": None,
        "prep_time_mins": None,
        "cook_time_mins": None,
        "equipment": [],
        "storage": None,
        "cost_per_serving_usd": None,
        "tags": [],
        "ingredients": [],
        "steps": [],
        "notes": None,
    }
    md = recipe_to_markdown(recipe)
    assert "# Quick Idea" in md
    assert "**Status:** draft" in md
    # Optional fields should be omitted, not show "None"
    assert "None" not in md
    assert "Cuisine" not in md
    assert "Servings" not in md
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_generate.py::test_recipe_to_markdown_full -v
```

Expected: FAIL — `ImportError`

- [ ] **Step 3: Write `recipe_to_markdown` function**

Create `scripts/generate.py`:

```python
"""Generates markdown docs and README from recipe YAML files."""

import argparse
from pathlib import Path

from loader import load_all_recipes, load_equipment


def recipe_to_markdown(recipe: dict) -> str:
    """Convert a recipe dict to a markdown string. Omits sections for missing fields."""
    lines = [f"# {recipe['name']}", ""]

    # Status always shown
    lines.append(f"**Status:** {recipe['status']}")

    # Optional metadata line
    meta = []
    if recipe["cuisine"]:
        meta.append(f"**Cuisine:** {recipe['cuisine']}")
    if recipe["category"]:
        meta.append(f"**Category:** {recipe['category']}")
    if recipe["servings"] is not None:
        meta.append(f"**Servings:** {recipe['servings']}")
    if recipe["prep_time_mins"] is not None:
        meta.append(f"**Prep:** {recipe['prep_time_mins']} mins")
    if recipe["cook_time_mins"] is not None:
        meta.append(f"**Cook:** {recipe['cook_time_mins']} mins")
    if recipe["cost_per_serving_usd"] is not None:
        meta.append(f"**Cost/serving:** ${recipe['cost_per_serving_usd']:.2f}")
    for item in meta:
        lines.append(item)

    if recipe["tags"]:
        lines.append(f"**Tags:** {', '.join(recipe['tags'])}")

    if recipe["equipment"]:
        lines.append(f"**Equipment:** {', '.join(recipe['equipment'])}")

    lines.append("")

    # Ingredients
    if recipe["ingredients"]:
        lines.append("## Ingredients")
        lines.append("")
        for ing in recipe["ingredients"]:
            qty = ing.get("qty", "")
            unit = ing.get("unit", "")
            item = ing["item"]
            if qty and unit:
                lines.append(f"- {qty} {unit} {item}")
            elif qty:
                lines.append(f"- {qty} {item}")
            else:
                lines.append(f"- {item}")
        lines.append("")

    # Steps
    if recipe["steps"]:
        lines.append("## Steps")
        lines.append("")
        for i, step in enumerate(recipe["steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    # Storage
    if recipe["storage"]:
        lines.append("## Storage")
        lines.append("")
        s = recipe["storage"]
        if s.get("fridge_days"):
            lines.append(f"**Fridge:** {s['fridge_days']} days")
        if s.get("freezer_days"):
            lines.append(f"**Freezer:** {s['freezer_days']} days")
        if s.get("reheating"):
            lines.append(f"**Reheating:** {s['reheating']}")
        lines.append("")

    # Notes
    if recipe["notes"]:
        lines.append("## Notes")
        lines.append("")
        lines.append(recipe["notes"])
        lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_generate.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: recipe_to_markdown function with tests"
```

---

### Task 4: README generation and warnings

**Files:**
- Modify: `scripts/generate.py`
- Modify: `tests/test_generate.py`

- [ ] **Step 1: Write failing test for README generation**

Add to `tests/test_generate.py`:

```python
from generate import generate_readme


def test_generate_readme():
    recipes = [
        {
            "name": "Chicken Tikka",
            "slug": "chicken-tikka",
            "status": "tested",
            "cuisine": "Indian",
            "category": "protein",
            "servings": 8,
            "prep_time_mins": 15,
            "cook_time_mins": 25,
            "equipment": ["instant-pot"],
            "storage": None,
            "cost_per_serving_usd": 1.50,
            "tags": ["high-protein"],
            "ingredients": [],
            "steps": [],
            "notes": None,
        },
        {
            "name": "Dal Tadka",
            "slug": "dal-tadka",
            "status": "draft",
            "cuisine": "Indian",
            "category": None,
            "servings": None,
            "prep_time_mins": None,
            "cook_time_mins": None,
            "equipment": [],
            "storage": None,
            "cost_per_serving_usd": None,
            "tags": ["vegetarian", "high-protein"],
            "ingredients": [],
            "steps": [],
            "notes": None,
        },
    ]
    equipment_ids = {"instant-pot", "air-fryer", "blender"}
    equipment_by_id = {
        "instant-pot": {"id": "instant-pot", "name": "Instant Pot Duo"},
        "air-fryer": {"id": "air-fryer", "name": "Gourmia Air Fryer"},
        "blender": {"id": "blender", "name": "Vitamix E Series"},
    }
    readme = generate_readme(recipes, equipment_ids, equipment_by_id)
    assert "# Recipe Engine" in readme
    assert "Chicken Tikka" in readme
    assert "Dal Tadka" in readme
    # Index table
    assert "| Name" in readme
    # Grouped by cuisine
    assert "### Indian" in readme
    # Grouped by status
    assert "### tested" in readme
    assert "### draft" in readme
    # Per-appliance section
    assert "Instant Pot Duo" in readme


def test_generate_readme_warns_unknown_equipment(capsys):
    recipes = [
        {
            "name": "Test",
            "slug": "test",
            "status": "draft",
            "cuisine": None,
            "category": None,
            "servings": None,
            "prep_time_mins": None,
            "cook_time_mins": None,
            "equipment": ["unknown-gadget"],
            "storage": None,
            "cost_per_serving_usd": None,
            "tags": [],
            "ingredients": [],
            "steps": [],
            "notes": None,
        },
    ]
    generate_readme(recipes, set(), {})
    captured = capsys.readouterr()
    assert "unknown-gadget" in captured.err
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_generate.py::test_generate_readme -v
```

Expected: FAIL — `ImportError`

- [ ] **Step 3: Write `generate_readme` function**

Add to `scripts/generate.py`:

```python
import sys
from collections import defaultdict


def generate_readme(
    recipes: list[dict],
    equipment_ids: set[str],
    equipment_by_id: dict[str, dict],
) -> str:
    """Generate README.md content with index table and grouped views."""
    lines = ["# Recipe Engine", ""]
    lines.append("Personal batch cooking recipe collection.")
    lines.append("")

    # Warnings for unknown equipment
    for r in recipes:
        for eid in r["equipment"]:
            if eid not in equipment_ids:
                print(
                    f"WARNING: Recipe '{r['name']}' references unknown equipment '{eid}'",
                    file=sys.stderr,
                )

    # Warn about missing servings when cost is present
    for r in recipes:
        if r["cost_per_serving_usd"] is not None and r["servings"] is None:
            print(
                f"WARNING: Recipe '{r['name']}' has cost_per_serving_usd but no servings",
                file=sys.stderr,
            )

    # Warn about recipes missing key fields (informational)
    for r in recipes:
        if not r["ingredients"]:
            print(
                f"INFO: Recipe '{r['name']}' has no ingredients",
                file=sys.stderr,
            )
        if not r["steps"]:
            print(
                f"INFO: Recipe '{r['name']}' has no steps",
                file=sys.stderr,
            )

    # Index table
    lines.append("## All Recipes")
    lines.append("")
    lines.append("| Name | Cuisine | Status | Prep | Cook | Cost/serving | Tags |")
    lines.append("|------|---------|--------|------|------|-------------|------|")
    for r in recipes:
        name_link = f"[{r['name']}](docs/{r['slug']}.md)"
        cuisine = r["cuisine"] or ""
        status = r["status"]
        prep = f"{r['prep_time_mins']}m" if r["prep_time_mins"] else ""
        cook = f"{r['cook_time_mins']}m" if r["cook_time_mins"] else ""
        cost = f"${r['cost_per_serving_usd']:.2f}" if r["cost_per_serving_usd"] else ""
        tags = ", ".join(r["tags"]) if r["tags"] else ""
        lines.append(f"| {name_link} | {cuisine} | {status} | {prep} | {cook} | {cost} | {tags} |")
    lines.append("")

    # Grouped by cuisine
    by_cuisine = defaultdict(list)
    for r in recipes:
        if r["cuisine"]:
            by_cuisine[r["cuisine"]].append(r)
    if by_cuisine:
        lines.append("## By Cuisine")
        lines.append("")
        for cuisine in sorted(by_cuisine):
            lines.append(f"### {cuisine}")
            lines.append("")
            for r in by_cuisine[cuisine]:
                lines.append(f"- [{r['name']}](docs/{r['slug']}.md)")
            lines.append("")

    # Grouped by status
    by_status = defaultdict(list)
    for r in recipes:
        by_status[r["status"]].append(r)
    lines.append("## By Status")
    lines.append("")
    for status in ["staple", "tested", "draft"]:
        if status in by_status:
            lines.append(f"### {status}")
            lines.append("")
            for r in by_status[status]:
                lines.append(f"- [{r['name']}](docs/{r['slug']}.md)")
            lines.append("")

    # Grouped by tag
    by_tag = defaultdict(list)
    for r in recipes:
        for tag in r["tags"]:
            by_tag[tag].append(r)
    if by_tag:
        lines.append("## By Tag")
        lines.append("")
        for tag in sorted(by_tag):
            lines.append(f"### {tag}")
            lines.append("")
            for r in by_tag[tag]:
                lines.append(f"- [{r['name']}](docs/{r['slug']}.md)")
            lines.append("")

    # Per-appliance sections
    by_equip = defaultdict(list)
    for r in recipes:
        for eid in r["equipment"]:
            if eid in equipment_ids:
                by_equip[eid].append(r)
    if by_equip:
        lines.append("## By Equipment")
        lines.append("")
        for eid in sorted(by_equip):
            equip_name = equipment_by_id[eid].get("name", eid)
            lines.append(f"### {equip_name}")
            lines.append("")
            for r in by_equip[eid]:
                lines.append(f"- [{r['name']}](docs/{r['slug']}.md)")
            lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_generate.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: README generation with index table, grouped views, and warnings"
```

---

### Task 5: CLI entry point for generate.py

**Files:**
- Modify: `scripts/generate.py`
- Modify: `tests/test_generate.py`

- [ ] **Step 1: Write failing integration test**

Add to `tests/test_generate.py`:

```python
import subprocess


def test_generate_cli_integration(tmp_path):
    """End-to-end test: run generate.py against sample recipes."""
    # Set up a mini repo structure
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (recipes_dir / "test-recipe.yaml").write_text(
        "name: Test Recipe\nstatus: tested\ncuisine: Indian\n"
        "servings: 4\ntags:\n  - quick\n"
    )
    equip_file = tmp_path / "equipment.yaml"
    equip_file.write_text(
        "appliances:\n  - id: instant-pot\n    name: Instant Pot\n"
    )

    script = Path(__file__).parent.parent / "scripts" / "generate.py"
    result = subprocess.run(
        ["python", str(script), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Check docs/test-recipe.md was created
    doc = (docs_dir / "test-recipe.md").read_text()
    assert "# Test Recipe" in doc

    # Check README.md was created
    readme = (tmp_path / "README.md").read_text()
    assert "Test Recipe" in readme
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_generate.py::test_generate_cli_integration -v
```

Expected: FAIL

- [ ] **Step 3: Add CLI main block to `generate.py`**

Add at the bottom of `scripts/generate.py`:

```python
def main():
    parser = argparse.ArgumentParser(description="Generate markdown docs from recipe YAML files")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root directory of the recipe-engine repo",
    )
    args = parser.parse_args()

    root = args.root
    recipes_dir = root / "recipes"
    docs_dir = root / "docs"
    equip_path = root / "equipment.yaml"

    docs_dir.mkdir(exist_ok=True)

    # Load data
    recipes = load_all_recipes(recipes_dir)
    equipment = load_equipment(equip_path)

    # Generate per-recipe markdown
    for recipe in recipes:
        md = recipe_to_markdown(recipe)
        (docs_dir / f"{recipe['slug']}.md").write_text(md)

    # Generate README
    readme = generate_readme(recipes, equipment["all_ids"], equipment["by_id"])
    (root / "README.md").write_text(readme)

    print(f"Generated docs for {len(recipes)} recipes.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all generate tests**

```bash
python -m pytest tests/test_generate.py -v
```

Expected: 5 passed

- [ ] **Step 5: Run generate.py against the real repo**

```bash
cd /Users/yashashav/jurisprudence/recipe-engine
python scripts/generate.py
```

Expected: `Generated docs for 2 recipes.` — verify `docs/chicken-tikka.md`, `docs/dal-tadka.md`, and `README.md` were created.

- [ ] **Step 6: Commit generated files**

```bash
git add scripts/generate.py tests/test_generate.py docs/ README.md
git commit -m "feat: generate.py CLI - produces docs and README from recipes"
```

---

## Chunk 3: Meal Planner (`meal_planner.py`)

### Task 6: Recipe filtering logic

**Files:**
- Create: `scripts/meal_planner.py`
- Create: `tests/test_meal_planner.py`

- [ ] **Step 1: Write failing tests for recipe filtering**

Create `tests/test_meal_planner.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from meal_planner import filter_recipes

RECIPES = [
    {
        "name": "Chicken Tikka",
        "slug": "chicken-tikka",
        "status": "tested",
        "cuisine": "Indian",
        "category": "protein",
        "servings": 8,
        "prep_time_mins": 15,
        "cook_time_mins": 25,
        "equipment": ["instant-pot"],
        "storage": {"fridge_days": 5, "freezer_days": 30},
        "cost_per_serving_usd": 1.50,
        "tags": ["high-protein", "meal-prep"],
        "ingredients": [],
        "steps": [],
        "notes": None,
    },
    {
        "name": "Dal Tadka",
        "slug": "dal-tadka",
        "status": "draft",
        "cuisine": "Indian",
        "category": None,
        "servings": 6,
        "prep_time_mins": None,
        "cook_time_mins": None,
        "equipment": ["instant-pot"],
        "storage": None,
        "cost_per_serving_usd": 0.80,
        "tags": ["vegetarian", "high-protein"],
        "ingredients": [],
        "steps": [],
        "notes": None,
    },
    {
        "name": "Smoothie",
        "slug": "smoothie",
        "status": "staple",
        "cuisine": None,
        "category": "drink",
        "servings": 2,
        "prep_time_mins": 5,
        "cook_time_mins": 0,
        "equipment": ["blender"],
        "storage": None,
        "cost_per_serving_usd": 2.00,
        "tags": ["quick"],
        "ingredients": [],
        "steps": [],
        "notes": None,
    },
]


def test_filter_by_status_default():
    """Default: exclude drafts."""
    result = filter_recipes(RECIPES)
    names = [r["name"] for r in result]
    assert "Dal Tadka" not in names
    assert "Chicken Tikka" in names
    assert "Smoothie" in names


def test_filter_by_status_explicit():
    result = filter_recipes(RECIPES, status=["draft"])
    names = [r["name"] for r in result]
    assert names == ["Dal Tadka"]


def test_filter_by_tags():
    result = filter_recipes(RECIPES, tags=["high-protein"])
    names = [r["name"] for r in result]
    assert "Chicken Tikka" in names
    # Dal Tadka has the tag but is draft (excluded by default)
    assert "Dal Tadka" not in names


def test_filter_by_equipment():
    result = filter_recipes(RECIPES, equipment=["blender"])
    names = [r["name"] for r in result]
    assert names == ["Smoothie"]


def test_filter_by_budget_skips_uncosted_recipes():
    """Budget filter excludes recipes that can't compute total cost."""
    recipes_with_missing = RECIPES + [
        {
            "name": "No Cost Info",
            "slug": "no-cost",
            "status": "tested",
            "cuisine": None,
            "category": None,
            "servings": None,
            "prep_time_mins": None,
            "cook_time_mins": None,
            "equipment": [],
            "storage": None,
            "cost_per_serving_usd": None,
            "tags": [],
            "ingredients": [],
            "steps": [],
            "notes": None,
        },
    ]
    result = filter_recipes(recipes_with_missing, max_budget_per_week=20.0)
    names = [r["name"] for r in result]
    assert "No Cost Info" not in names
    assert "Chicken Tikka" in names
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_meal_planner.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write filter_recipes function**

Create `scripts/meal_planner.py`:

```python
"""Weekly batch cooking meal planner CLI."""

import argparse
import random
from collections import defaultdict
from pathlib import Path
from typing import Optional

from loader import load_all_recipes, load_equipment


def filter_recipes(
    recipes: list[dict],
    status: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    equipment: Optional[list[str]] = None,
    max_budget_per_week: Optional[float] = None,
) -> list[dict]:
    """Filter recipes by status, tags, equipment. Budget filtering skips recipes without servings."""
    if status is None:
        # Default: exclude drafts
        status = ["tested", "staple"]

    filtered = [r for r in recipes if r["status"] in status]

    if tags:
        filtered = [r for r in filtered if any(t in r["tags"] for t in tags)]

    if equipment:
        filtered = [
            r for r in filtered if any(e in r["equipment"] for e in equipment)
        ]

    if max_budget_per_week is not None:
        # Skip recipes that can't compute total cost
        filtered = [
            r for r in filtered
            if r["servings"] is not None and r["cost_per_serving_usd"] is not None
        ]

    return filtered
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_meal_planner.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/meal_planner.py tests/test_meal_planner.py
git commit -m "feat: recipe filtering for meal planner"
```

---

### Task 7: Meal selection and shopping list

**Files:**
- Modify: `scripts/meal_planner.py`
- Modify: `tests/test_meal_planner.py`

- [ ] **Step 1: Write failing tests for meal selection**

Add to `tests/test_meal_planner.py`:

```python
from meal_planner import select_meals, build_shopping_list


def test_select_meals_fills_servings():
    recipes = [
        {"name": "A", "servings": 4, "cost_per_serving_usd": 1.0, "tags": []},
        {"name": "B", "servings": 6, "cost_per_serving_usd": 1.5, "tags": []},
        {"name": "C", "servings": 8, "cost_per_serving_usd": 2.0, "tags": []},
    ]
    random.seed(42)
    selected = select_meals(recipes, servings_per_day=3)
    total_servings = sum(r["servings"] for r in selected)
    # 3 servings/day * 7 days = 21 target
    assert total_servings >= 21


def test_select_meals_respects_budget():
    recipes = [
        {"name": "Cheap", "servings": 10, "cost_per_serving_usd": 0.50, "tags": []},
        {"name": "Expensive", "servings": 10, "cost_per_serving_usd": 5.00, "tags": []},
    ]
    random.seed(42)
    selected = select_meals(recipes, servings_per_day=2, max_budget=15.0)
    total_cost = sum(r["servings"] * r["cost_per_serving_usd"] for r in selected)
    assert total_cost <= 15.0


def test_select_meals_avoids_unnecessary_repeats():
    """When enough unique recipes exist to meet target, no repeats needed."""
    recipes = [
        {"name": "A", "servings": 10, "cost_per_serving_usd": 1.0, "tags": []},
        {"name": "B", "servings": 10, "cost_per_serving_usd": 1.0, "tags": []},
        {"name": "C", "servings": 10, "cost_per_serving_usd": 1.0, "tags": []},
    ]
    random.seed(42)
    selected = select_meals(recipes, servings_per_day=3)
    names = [r["name"] for r in selected]
    # 30 servings available from 3 unique recipes, only need 21 — no repeats needed
    assert len(names) == len(set(names))


def test_build_shopping_list():
    selected = [
        {
            "name": "A",
            "ingredients": [
                {"item": "chicken thighs", "qty": 500, "unit": "g"},
                {"item": "yogurt", "qty": 250, "unit": "ml"},
            ],
        },
        {
            "name": "B",
            "ingredients": [
                {"item": "chicken thighs", "qty": 300, "unit": "g"},
                {"item": "rice", "qty": 500, "unit": "g"},
            ],
        },
    ]
    shopping = build_shopping_list(selected)
    assert shopping[("chicken thighs", "g")] == 800
    assert shopping[("yogurt", "ml")] == 250
    assert shopping[("rice", "g")] == 500
```

Add `import random` to the top of the test file.

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_meal_planner.py::test_select_meals_fills_servings -v
```

Expected: FAIL — `ImportError`

- [ ] **Step 3: Write `select_meals` and `build_shopping_list`**

Add to `scripts/meal_planner.py`:

```python
def select_meals(
    recipes: list[dict],
    servings_per_day: int = 3,
    max_budget: Optional[float] = None,
) -> list[dict]:
    """Pick recipes to fill weekly servings target. Random selection, avoids repeats when possible."""
    target_servings = servings_per_day * 7
    selected = []
    current_servings = 0
    current_cost = 0.0
    available = list(recipes)
    random.shuffle(available)

    for recipe in available:
        if current_servings >= target_servings:
            break
        recipe_cost = recipe["servings"] * recipe["cost_per_serving_usd"]
        if max_budget is not None and current_cost + recipe_cost > max_budget:
            continue
        selected.append(recipe)
        current_servings += recipe["servings"]
        current_cost += recipe_cost

    # If we haven't hit target, repeat recipes until target met or no progress possible
    while current_servings < target_servings:
        made_progress = False
        pool = list(recipes)
        random.shuffle(pool)
        for recipe in pool:
            if current_servings >= target_servings:
                break
            recipe_cost = recipe["servings"] * recipe["cost_per_serving_usd"]
            if max_budget is not None and current_cost + recipe_cost > max_budget:
                continue
            selected.append(recipe)
            current_servings += recipe["servings"]
            current_cost += recipe_cost
            made_progress = True
        if not made_progress:
            break

    return selected


def build_shopping_list(selected: list[dict]) -> dict[tuple[str, str], float]:
    """Combine ingredients across selected recipes. Dedup by exact (item, unit) match."""
    shopping = defaultdict(float)
    for recipe in selected:
        for ing in recipe.get("ingredients", []):
            key = (ing["item"], ing.get("unit", ""))
            shopping[key] += ing.get("qty", 0)
    return dict(shopping)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_meal_planner.py -v
```

Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/meal_planner.py tests/test_meal_planner.py
git commit -m "feat: meal selection algorithm and shopping list builder"
```

---

### Task 8: Output formatting and CLI

**Files:**
- Modify: `scripts/meal_planner.py`
- Modify: `tests/test_meal_planner.py`

- [ ] **Step 1: Write failing test for formatted output**

Add to `tests/test_meal_planner.py`:

```python
from meal_planner import format_plan


def test_format_plan():
    selected = [
        {
            "name": "Chicken Tikka",
            "servings": 8,
            "prep_time_mins": 15,
            "cook_time_mins": 25,
            "cost_per_serving_usd": 1.50,
            "storage": {"fridge_days": 5, "freezer_days": 30},
            "ingredients": [
                {"item": "chicken thighs", "qty": 900, "unit": "g"},
                {"item": "yogurt", "qty": 250, "unit": "ml"},
            ],
        },
    ]
    output = format_plan(selected)
    assert "Chicken Tikka" in output
    assert "Shopping List" in output
    assert "900 g chicken thighs" in output
    assert "Cook Schedule" in output
    assert "Storage Plan" in output
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_meal_planner.py::test_format_plan -v
```

Expected: FAIL

- [ ] **Step 3: Write `format_plan` function**

Add to `scripts/meal_planner.py`:

```python
def format_plan(selected: list[dict]) -> str:
    """Format the meal plan as readable text output."""
    lines = ["=" * 50, "WEEKLY BATCH COOKING PLAN", "=" * 50, ""]

    # Cook schedule
    lines.append("## Cook Schedule")
    lines.append("")
    total_prep = 0
    total_cook = 0
    total_cost = 0.0
    total_servings = 0
    for i, r in enumerate(selected, 1):
        prep = r.get("prep_time_mins") or 0
        cook = r.get("cook_time_mins") or 0
        cost = (r.get("cost_per_serving_usd") or 0) * (r.get("servings") or 0)
        total_prep += prep
        total_cook += cook
        total_cost += cost
        total_servings += r.get("servings") or 0
        lines.append(f"{i}. {r['name']}")
        lines.append(f"   Servings: {r.get('servings', '?')}")
        if prep or cook:
            lines.append(f"   Time: {prep}m prep + {cook}m cook = {prep + cook}m total")
        if r.get("cost_per_serving_usd"):
            lines.append(f"   Cost: ${cost:.2f} total (${r['cost_per_serving_usd']:.2f}/serving)")
        lines.append("")

    lines.append(f"**Totals:** {total_servings} servings, {total_prep + total_cook}m cooking time, ${total_cost:.2f}")
    lines.append("")

    # Shopping list
    shopping = build_shopping_list(selected)
    lines.append("## Shopping List")
    lines.append("")
    for (item, unit), qty in sorted(shopping.items()):
        if unit:
            lines.append(f"- {qty:g} {unit} {item}")
        else:
            lines.append(f"- {qty:g} {item}")
    lines.append("")

    # Storage plan
    lines.append("## Storage Plan")
    lines.append("")
    for r in selected:
        storage = r.get("storage")
        if storage:
            fridge = storage.get("fridge_days", "?")
            freezer = storage.get("freezer_days", "?")
            lines.append(f"- {r['name']}: fridge {fridge} days, freezer {freezer} days")
        else:
            lines.append(f"- {r['name']}: no storage info (check after cooking)")
    lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_meal_planner.py -v
```

Expected: 9 passed

- [ ] **Step 5: Write CLI integration test**

Add to `tests/test_meal_planner.py`:

```python
import subprocess


def test_meal_planner_cli_integration(tmp_path):
    """End-to-end test: run meal_planner.py against sample recipes."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    (recipes_dir / "test-meal.yaml").write_text(
        "name: Test Meal\nstatus: tested\nservings: 8\n"
        "cost_per_serving_usd: 1.50\n"
        "ingredients:\n  - item: rice\n    qty: 500\n    unit: g\n"
    )
    equip_file = tmp_path / "equipment.yaml"
    equip_file.write_text(
        "appliances:\n  - id: instant-pot\n    name: Instant Pot\n"
    )

    script = Path(__file__).parent.parent / "scripts" / "meal_planner.py"
    result = subprocess.run(
        ["python", str(script), "--root", str(tmp_path), "--seed", "42"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "WEEKLY BATCH COOKING PLAN" in result.stdout
    assert "Test Meal" in result.stdout
    assert "Shopping List" in result.stdout
```

- [ ] **Step 7: Write CLI main block**

Add at the bottom of `scripts/meal_planner.py`:

```python
def main():
    parser = argparse.ArgumentParser(description="Generate a weekly batch cooking meal plan")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root directory of the recipe-engine repo",
    )
    parser.add_argument("--equipment", nargs="+", help="Only recipes using this equipment")
    parser.add_argument("--tags", nargs="+", help="Only recipes with these tags")
    parser.add_argument("--status", nargs="+", help="Recipe statuses to include (default: tested, staple)")
    parser.add_argument("--max-budget-per-week", type=float, help="Maximum weekly budget in USD")
    parser.add_argument("--servings-per-day", type=int, default=3, help="Target servings per day (default: 3)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible plans")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    root = args.root
    recipes = load_all_recipes(root / "recipes")

    filtered = filter_recipes(
        recipes,
        status=args.status,
        tags=args.tags,
        equipment=args.equipment,
        max_budget_per_week=args.max_budget_per_week,
    )

    if not filtered:
        print("No recipes match your filters.")
        return

    selected = select_meals(
        filtered,
        servings_per_day=args.servings_per_day,
        max_budget=args.max_budget_per_week,
    )

    print(format_plan(selected))


if __name__ == "__main__":
    main()
```

- [ ] **Step 8: Run meal planner against the real repo**

```bash
cd /Users/yashashav/jurisprudence/recipe-engine
python scripts/meal_planner.py --status tested staple
```

Expected: A formatted weekly plan using Chicken Tikka (the only non-draft recipe).

- [ ] **Step 9: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 10: Commit**

```bash
git add scripts/meal_planner.py tests/test_meal_planner.py
git commit -m "feat: meal planner CLI with formatted output"
```

---

## Chunk 4: Final Integration

### Task 9: Final integration and push

**Note:** GitHub repo already created at https://github.com/yashashav-dk/recipe-engine (private). Remote `origin` is configured.

**Files:**
- All files in repo

- [ ] **Step 1: Run generate.py to produce final docs**

```bash
python scripts/generate.py
```

- [ ] **Step 2: Run all tests one final time**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 3: Commit generated docs**

```bash
git add docs/ README.md
git commit -m "docs: generate initial recipe docs and README"
```

- [ ] **Step 4: Push to GitHub**

```bash
git push
```

- [ ] **Step 5: Verify on GitHub**

Check https://github.com/yashashav-dk/recipe-engine — README should render with the recipe index and grouped views.
