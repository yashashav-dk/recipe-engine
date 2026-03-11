"""Weekly batch cooking meal planner CLI."""

import argparse
import random
from collections import defaultdict
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from loader import load_all_recipes, load_equipment


def filter_recipes(
    recipes,
    status=None,
    tags=None,
    equipment=None,
    max_budget_per_week=None,
):
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


def select_meals(
    recipes,
    servings_per_day=3,
    max_budget=None,
):
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


def build_shopping_list(selected):
    """Combine ingredients across selected recipes. Dedup by exact (item, unit) match."""
    shopping = defaultdict(float)
    for recipe in selected:
        for ing in recipe.get("ingredients", []):
            key = (ing["item"], ing.get("unit", ""))
            shopping[key] += ing.get("qty", 0)
    return dict(shopping)


def format_plan(selected):
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
