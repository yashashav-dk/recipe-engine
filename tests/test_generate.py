import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate import recipe_to_markdown, generate_readme


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


import subprocess
import sys


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
        [sys.executable, str(script), "--root", str(tmp_path)],
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
