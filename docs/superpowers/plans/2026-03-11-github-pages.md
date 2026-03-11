# GitHub Pages Recipe Site Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a static GitHub Pages site that renders YAML recipes as a browsable website with checkable ingredients for cooking mode.

**Architecture:** Extend `generate.py` to output HTML (via Jinja2 templates) alongside markdown. Homepage is a grouped list by cuisine; each recipe gets a detail page with interactive ingredient checkboxes. GitHub Pages serves from `docs/`.

**Tech Stack:** Python 3.8+, PyYAML, Jinja2, vanilla HTML/CSS/JS

**Spec:** `docs/superpowers/specs/2026-03-11-github-pages-design.md`

**Prerequisite:** The core recipe-engine plan (`docs/superpowers/plans/2026-03-11-recipe-engine.md`) must be executed first. This plan assumes `scripts/loader.py`, `scripts/generate.py`, and `tests/` already exist and work.

---

## Chunk 1: Templates, Stylesheet, and Static Files

### Task 1: Add Jinja2 dependency and static files

**Files:**
- Modify: `requirements.txt`
- Create: `docs/.nojekyll`
- Create: `scripts/static/style.css`

- [ ] **Step 1: Update `requirements.txt`**

```
pyyaml
jinja2
```

- [ ] **Step 2: Install dependencies**

```bash
cd /Users/yashashav/jurisprudence/recipe-engine
pip install -r requirements.txt
```

- [ ] **Step 3: Create `docs/.nojekyll`**

Empty file to disable Jekyll processing on GitHub Pages:

```bash
touch docs/.nojekyll
```

- [ ] **Step 4: Create `scripts/static/style.css`**

```css
/* Recipe Engine — Dark theme, mobile-first */

:root {
  --bg: #1a1a2e;
  --bg-card: #16213e;
  --bg-hover: #0f3460;
  --text: #e0e0e0;
  --text-muted: #888;
  --text-dim: #555;
  --accent: #ff9f43;
  --green: #2ecc71;
  --orange: #ff9f43;
  --gray: #666;
  --border: #333;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 16px;
  max-width: 700px;
  margin: 0 auto;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Header */
.site-header {
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}

.site-header h1 {
  color: var(--accent);
  font-size: 1.5rem;
}

/* Cuisine group */
.cuisine-group {
  margin-bottom: 24px;
}

.cuisine-group h2 {
  color: var(--accent);
  font-size: 1.1rem;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}

/* Recipe list row */
.recipe-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-card);
  border-radius: 4px;
  margin-bottom: 4px;
}

.recipe-row:hover {
  background: var(--bg-hover);
}

.recipe-row a {
  color: var(--text);
  flex: 1;
}

.recipe-row.draft a {
  color: var(--text-dim);
}

.recipe-meta {
  display: flex;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* Status badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
}

.badge-staple {
  background: var(--green);
  color: #000;
}

.badge-tested {
  background: var(--orange);
  color: #000;
}

.badge-draft {
  background: var(--gray);
  color: #fff;
}

/* Recipe detail page */
.back-link {
  display: inline-block;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.recipe-title {
  color: var(--accent);
  font-size: 1.5rem;
  margin-bottom: 12px;
}

.recipe-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.meta-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  background: var(--border);
}

/* Sections */
.section {
  margin-bottom: 24px;
}

.section h2 {
  color: var(--accent);
  font-size: 1rem;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Checkable ingredients */
.ingredient {
  display: flex;
  align-items: center;
  padding: 6px 0;
  cursor: pointer;
  user-select: none;
}

.ingredient input[type="checkbox"] {
  margin-right: 10px;
  accent-color: var(--accent);
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.ingredient.checked label {
  text-decoration: line-through;
  color: var(--text-muted);
}

.ingredient label {
  cursor: pointer;
  font-size: 1rem;
}

/* Steps */
.steps {
  padding-left: 24px;
}

.steps li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* Storage */
.storage-info p {
  margin-bottom: 4px;
}

/* Notes */
.notes {
  background: var(--bg-card);
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid var(--accent);
  line-height: 1.5;
}
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt docs/.nojekyll scripts/static/style.css
git commit -m "feat: add jinja2 dependency, stylesheet, and .nojekyll"
```

---

### Task 2: Jinja2 templates

**Files:**
- Create: `scripts/templates/index.html`
- Create: `scripts/templates/recipe.html`

- [ ] **Step 1: Create homepage template**

Create `scripts/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recipe Engine</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="site-header">
    <h1>Recipe Engine</h1>
  </div>

  {% for cuisine, recipes in groups %}
  <div class="cuisine-group">
    <h2>{{ cuisine }}</h2>
    {% for recipe in recipes %}
    <div class="recipe-row{% if recipe.status == 'draft' %} draft{% endif %}">
      <a href="recipes/{{ recipe.slug }}.html">{{ recipe.name }}</a>
      <div class="recipe-meta">
        <span class="badge badge-{{ recipe.status }}">{{ recipe.status }}</span>
        {% if recipe.prep_time_mins is not none or recipe.cook_time_mins is not none %}
        <span>{{ (recipe.prep_time_mins or 0) + (recipe.cook_time_mins or 0) }}m</span>
        {% endif %}
        {% if recipe.cost_per_serving_usd is not none %}
        <span>${{ "%.2f"|format(recipe.cost_per_serving_usd) }}</span>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endfor %}
</body>
</html>
```

- [ ] **Step 2: Create recipe detail template**

Create `scripts/templates/recipe.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ recipe.name }} — Recipe Engine</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <a href="../index.html" class="back-link">← all recipes</a>
  <h1 class="recipe-title">{{ recipe.name }}</h1>

  <div class="recipe-badges">
    <span class="badge badge-{{ recipe.status }}">{{ recipe.status }}</span>
    {% if recipe.cuisine %}<span class="meta-badge">{{ recipe.cuisine }}</span>{% endif %}
    {% if recipe.category %}<span class="meta-badge">{{ recipe.category }}</span>{% endif %}
    {% for tag in recipe.tags %}<span class="meta-badge">{{ tag }}</span>{% endfor %}
    {% if recipe.prep_time_mins is not none %}<span class="meta-badge">⏱ {{ recipe.prep_time_mins }}m prep</span>{% endif %}
    {% if recipe.cook_time_mins is not none %}<span class="meta-badge">🍳 {{ recipe.cook_time_mins }}m cook</span>{% endif %}
    {% if recipe.cost_per_serving_usd is not none %}<span class="meta-badge">💰 ${{ "%.2f"|format(recipe.cost_per_serving_usd) }}/srv</span>{% endif %}
    {% if recipe.servings is not none %}<span class="meta-badge">🍽 {{ recipe.servings }} servings</span>{% endif %}
    {% for e in recipe.equipment %}<span class="meta-badge">{{ e }}</span>{% endfor %}
  </div>

  {% if recipe.ingredients %}
  <div class="section">
    <h2>Ingredients</h2>
    {% for ing in recipe.ingredients %}
    <div class="ingredient" onclick="this.classList.toggle('checked'); this.querySelector('input').checked = this.classList.contains('checked');">
      <input type="checkbox" tabindex="-1">
      <label>
        {%- if ing.qty is defined and ing.qty %}{{ ing.qty }} {% endif %}
        {%- if ing.unit is defined and ing.unit %}{{ ing.unit }} {% endif %}
        {{- ing.item -}}
      </label>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if recipe.steps %}
  <div class="section">
    <h2>Steps</h2>
    <ol class="steps">
      {% for step in recipe.steps %}
      <li>{{ step }}</li>
      {% endfor %}
    </ol>
  </div>
  {% endif %}

  {% if recipe.storage %}
  <div class="section">
    <h2>Storage</h2>
    <div class="storage-info">
      {% if recipe.storage.fridge_days %}<p><strong>Fridge:</strong> {{ recipe.storage.fridge_days }} days</p>{% endif %}
      {% if recipe.storage.freezer_days %}<p><strong>Freezer:</strong> {{ recipe.storage.freezer_days }} days</p>{% endif %}
      {% if recipe.storage.reheating %}<p><strong>Reheating:</strong> {{ recipe.storage.reheating }}</p>{% endif %}
    </div>
  </div>
  {% endif %}

  {% if recipe.notes %}
  <div class="section">
    <h2>Notes</h2>
    <div class="notes">{{ recipe.notes }}</div>
  </div>
  {% endif %}
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add scripts/templates/index.html scripts/templates/recipe.html
git commit -m "feat: add Jinja2 templates for homepage and recipe detail"
```

---

## Chunk 2: Extend generate.py for HTML Output

### Task 3: HTML generation functions

**Files:**
- Modify: `scripts/generate.py`
- Modify: `tests/test_generate.py`

- [ ] **Step 1: Write failing test for HTML recipe page generation**

Add to `tests/test_generate.py`:

```python
from generate import generate_recipe_html, generate_index_html


def test_generate_recipe_html():
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
        "tags": ["high-protein", "spicy"],
        "ingredients": [
            {"item": "chicken breast", "qty": 800, "unit": "g"},
            {"item": "yogurt", "qty": 250, "unit": "ml"},
            {"item": "onion", "qty": 2},
        ],
        "steps": [
            "Cut chicken into chunks",
            "Marinate in yogurt",
        ],
        "notes": "Day 2-3 tastes best.",
    }
    html = generate_recipe_html(recipe)
    assert "<!DOCTYPE html>" in html
    assert "<title>Chicken Tikka" in html
    assert "<title>Chicken Tikka" in html
    assert "tested" in html
    assert "Indian" in html
    assert "800 g chicken breast" in html
    assert "250 ml yogurt" in html
    assert "2 onion" in html  # qty without unit
    assert "checkbox" in html
    assert "Cut chicken into chunks" in html
    assert "Fridge" in html
    assert "Day 2-3 tastes best." in html
    assert 'href="../style.css"' in html
    assert 'href="../index.html"' in html
    assert "viewport" in html
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_generate.py::test_generate_recipe_html -v
```

Expected: FAIL — `ImportError: cannot import name 'generate_recipe_html'`

- [ ] **Step 3: Write `generate_recipe_html` function**

Add these imports at the top of `scripts/generate.py` (note: `defaultdict` is already imported from the core plan — do not duplicate it):

```python
import shutil
from jinja2 import Environment, FileSystemLoader


def _get_jinja_env():
    """Create Jinja2 environment pointing at scripts/templates/."""
    templates_dir = Path(__file__).parent / "templates"
    return Environment(loader=FileSystemLoader(str(templates_dir)))


def generate_recipe_html(recipe: dict) -> str:
    """Render a single recipe as an HTML page using the recipe.html template."""
    env = _get_jinja_env()
    template = env.get_template("recipe.html")
    return template.render(recipe=recipe)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_generate.py::test_generate_recipe_html -v
```

Expected: PASS

- [ ] **Step 5: Write test for minimal recipe HTML (empty optional fields)**

Add to `tests/test_generate.py`:

```python
def test_generate_recipe_html_minimal():
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
    html = generate_recipe_html(recipe)
    assert "Quick Idea" in html
    assert "draft" in html
    # Optional sections should not appear
    assert "Ingredients" not in html
    assert "Steps" not in html
    assert "Storage" not in html
    assert "Notes" not in html
    assert "None" not in html
```

- [ ] **Step 6: Run both recipe HTML tests**

```bash
python -m pytest tests/test_generate.py -k "test_generate_recipe_html" -v
```

Expected: 2 passed

- [ ] **Step 7: Write failing test for index HTML generation**

Add to `tests/test_generate.py`:

```python
def test_generate_index_html():
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
            "equipment": [],
            "storage": None,
            "cost_per_serving_usd": 1.50,
            "tags": [],
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
            "equipment": [],
            "storage": None,
            "cost_per_serving_usd": 2.00,
            "tags": [],
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
            "tags": [],
            "ingredients": [],
            "steps": [],
            "notes": None,
        },
    ]
    html = generate_index_html(recipes)
    assert "<!DOCTYPE html>" in html
    assert "Recipe Engine" in html
    assert "Indian" in html
    assert "Other" in html  # Smoothie has no cuisine
    assert "Chicken Tikka" in html
    assert "Smoothie" in html
    assert "Dal Tadka" in html
    assert "draft" in html
    assert 'href="recipes/chicken-tikka.html"' in html
    assert "viewport" in html
```

- [ ] **Step 8: Write `generate_index_html` function**

Add to `scripts/generate.py` (note: `defaultdict` is already imported from the core plan — do not add it again):

```python
STATUS_ORDER = {"staple": 0, "tested": 1, "draft": 2}


def generate_index_html(recipes: list[dict]) -> str:
    """Render the homepage HTML with recipes grouped by cuisine."""
    env = _get_jinja_env()
    template = env.get_template("index.html")

    # Group by cuisine
    by_cuisine = defaultdict(list)
    for r in recipes:
        cuisine = r["cuisine"] or "Other"
        by_cuisine[cuisine].append(r)

    # Sort within each group: by status order, then alphabetically
    for cuisine in by_cuisine:
        by_cuisine[cuisine].sort(
            key=lambda r: (STATUS_ORDER.get(r["status"], 9), r["name"])
        )

    # Sort cuisine groups alphabetically, but "Other" goes last
    groups = sorted(
        by_cuisine.items(),
        key=lambda x: (x[0] == "Other", x[0]),
    )

    return template.render(groups=groups)
```

- [ ] **Step 9: Run test to verify it passes**

```bash
python -m pytest tests/test_generate.py::test_generate_index_html -v
```

Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: HTML generation functions for recipe pages and index"
```

---

### Task 4: Update generate.py CLI to output HTML

**Files:**
- Modify: `scripts/generate.py` (the `main()` function)
- Modify: `tests/test_generate.py`

- [ ] **Step 1: Write failing integration test for HTML output**

Add to `tests/test_generate.py`:

```python
def test_generate_cli_outputs_html(tmp_path):
    """End-to-end: generate.py produces HTML files alongside markdown."""
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "superpowers").mkdir(parents=True)  # simulate existing dir
    (recipes_dir / "test-recipe.yaml").write_text(
        "name: Test Recipe\nstatus: tested\ncuisine: Indian\n"
        "servings: 4\ncost_per_serving_usd: 1.50\n"
        "ingredients:\n  - item: rice\n    qty: 500\n    unit: g\n"
        "steps:\n  - Cook rice\n"
    )
    equip_file = tmp_path / "equipment.yaml"
    equip_file.write_text(
        "appliances:\n  - id: instant-pot\n    name: Instant Pot\n"
    )
    # Note: _get_jinja_env() and static copy resolve templates/static relative to
    # the real generate.py location (Path(__file__).parent), not relative to --root.
    # So no symlinks needed in tmp_path — the real scripts dir is used.
    script = Path(__file__).parent.parent / "scripts" / "generate.py"
    result = subprocess.run(
        ["python", str(script), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # HTML files created
    assert (docs_dir / "index.html").exists()
    assert (docs_dir / "recipes" / "test-recipe.html").exists()
    assert (docs_dir / "style.css").exists()

    # Markdown files in new location
    assert (docs_dir / "recipes" / "test-recipe.md").exists()

    # Check HTML content
    html = (docs_dir / "recipes" / "test-recipe.html").read_text()
    assert "Test Recipe" in html
    assert "checkbox" in html
    assert "500 g rice" in html

    # Check index
    index = (docs_dir / "index.html").read_text()
    assert "Test Recipe" in index
    assert "Indian" in index

    # Check README has site link
    readme = (tmp_path / "README.md").read_text()
    assert "Test Recipe" in readme
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_generate.py::test_generate_cli_outputs_html -v
```

Expected: FAIL

- [ ] **Step 3: Update `main()` in `generate.py`**

Replace the existing `main()` function in `scripts/generate.py`:

```python
def main():
    parser = argparse.ArgumentParser(description="Generate markdown docs and HTML site from recipe YAML files")
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
    recipes_docs_dir = docs_dir / "recipes"
    equip_path = root / "equipment.yaml"
    static_dir = Path(__file__).parent / "static"

    docs_dir.mkdir(exist_ok=True)
    recipes_docs_dir.mkdir(exist_ok=True)

    # Load data
    recipes = load_all_recipes(recipes_dir)
    equipment = load_equipment(equip_path)

    # Generate per-recipe markdown (now in docs/recipes/)
    for recipe in recipes:
        md = recipe_to_markdown(recipe)
        (recipes_docs_dir / f"{recipe['slug']}.md").write_text(md)

    # Generate per-recipe HTML
    for recipe in recipes:
        html = generate_recipe_html(recipe)
        (recipes_docs_dir / f"{recipe['slug']}.html").write_text(html)

    # Generate index HTML
    index_html = generate_index_html(recipes)
    (docs_dir / "index.html").write_text(index_html)

    # Copy static assets
    if static_dir.exists():
        for f in static_dir.iterdir():
            shutil.copy2(f, docs_dir / f.name)

    # Generate README
    readme = generate_readme(recipes, equipment["all_ids"], equipment["by_id"])
    (root / "README.md").write_text(readme)

    print(f"Generated docs for {len(recipes)} recipes.")
```

- [ ] **Step 4: Replace `generate_readme` function entirely**

This is a **breaking change** from the core plan's version. Replace the entire `generate_readme` function in `scripts/generate.py` with this version (changes: site link at top, all markdown links now point to `docs/recipes/<slug>.md`, informational warnings for missing fields):

```python
def generate_readme(
    recipes: list[dict],
    equipment_ids: set[str],
    equipment_by_id: dict[str, dict],
) -> str:
    """Generate README.md content with index table and grouped views."""
    lines = ["# Recipe Engine", ""]
    lines.append("[View recipe site](https://yashashav-dk.github.io/recipe-engine/)")
    lines.append("")
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
        name_link = f"[{r['name']}](docs/recipes/{r['slug']}.md)"
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
                lines.append(f"- [{r['name']}](docs/recipes/{r['slug']}.md)")
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
                lines.append(f"- [{r['name']}](docs/recipes/{r['slug']}.md)")
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
                lines.append(f"- [{r['name']}](docs/recipes/{r['slug']}.md)")
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
                lines.append(f"- [{r['name']}](docs/recipes/{r['slug']}.md)")
            lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 5: Update existing test assertions for new link paths**

In `tests/test_generate.py`, update `test_generate_readme` to expect the new link format and site link. Change these assertions:

```python
    # Old: assert "[Chicken Tikka](docs/chicken-tikka.md)" in readme
    # New:
    assert "docs/recipes/chicken-tikka.md" in readme
    assert "docs/recipes/dal-tadka.md" in readme
    assert "yashashav-dk.github.io/recipe-engine" in readme
```

Also update `test_generate_cli_integration` to check the new markdown path:

```python
    # Old: doc = (docs_dir / "test-recipe.md").read_text()
    # New:
    doc = (docs_dir / "recipes" / "test-recipe.md").read_text()
    assert "# Test Recipe" in doc
```

- [ ] **Step 6: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All pass.

- [ ] **Step 7: Commit**

```bash
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: generate.py outputs HTML site alongside markdown"
```

---

## Chunk 3: Migration, Deployment, and Verification

### Task 5: Migrate existing files and generate site

**Files:**
- Move: `docs/spicy-chicken-tikka-masala.md` → `docs/recipes/spicy-chicken-tikka-masala.md`
- Generate: all HTML + markdown

- [ ] **Step 1: Move existing markdown to new location**

```bash
mkdir -p docs/recipes
git mv docs/spicy-chicken-tikka-masala.md docs/recipes/spicy-chicken-tikka-masala.md
```

- [ ] **Step 2: Run generate.py**

```bash
python scripts/generate.py
```

Expected: `Generated docs for 1 recipes.` (or however many exist). Verify:
- `docs/index.html` exists
- `docs/recipes/spicy-chicken-tikka-masala.html` exists
- `docs/recipes/spicy-chicken-tikka-masala.md` exists (regenerated)
- `docs/style.css` exists
- `README.md` updated with site link

- [ ] **Step 3: Verify HTML looks correct locally**

```bash
open docs/index.html
```

Check in browser:
- Homepage shows recipe grouped under "Indian"
- Click recipe → detail page loads
- Ingredients have checkboxes that toggle on click
- Back link works
- Dark theme renders properly
- Mobile-friendly (resize browser window)

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All pass.

- [ ] **Step 5: Commit all generated files**

```bash
git add docs/ README.md
git commit -m "feat: generate initial HTML site with recipe pages"
```

---

### Task 6: Deploy to GitHub Pages

**Files:**
- No new files — deployment configuration only

- [ ] **Step 1: Make repo public**

```bash
gh repo edit --visibility public
```

Confirm when prompted.

- [ ] **Step 2: Enable GitHub Pages**

```bash
gh api repos/yashashav-dk/recipe-engine/pages -X POST -f source.branch=main -f source.path=/docs
```

If Pages is already enabled or the API doesn't support this, do it manually:
- Go to https://github.com/yashashav-dk/recipe-engine/settings/pages
- Source: Deploy from a branch
- Branch: `main`, folder: `/docs`
- Save

- [ ] **Step 3: Push to GitHub**

```bash
git push
```

- [ ] **Step 4: Verify deployment**

Wait 1-2 minutes for GitHub Pages to build, then check:

```bash
open https://yashashav-dk.github.io/recipe-engine/
```

Verify:
- Homepage loads with recipe list
- Click through to recipe detail page
- Ingredient checkboxes work
- Styling looks correct on mobile (use browser dev tools or actual phone)

- [ ] **Step 5: Commit any final fixes if needed**

If anything needed fixing after deployment verification:

```bash
git add -A
git commit -m "fix: adjust site for GitHub Pages deployment"
git push
```
