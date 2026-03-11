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
