import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from meal_planner import filter_recipes, select_meals, build_shopping_list

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


def test_meal_planner_cli_integration(tmp_path):
    """End-to-end test: run meal_planner.py against sample recipes."""
    import subprocess
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
        [sys.executable, str(script), "--root", str(tmp_path), "--seed", "42"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "WEEKLY BATCH COOKING PLAN" in result.stdout
    assert "Test Meal" in result.stdout
    assert "Shopping List" in result.stdout
