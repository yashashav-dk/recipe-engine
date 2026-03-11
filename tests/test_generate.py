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
