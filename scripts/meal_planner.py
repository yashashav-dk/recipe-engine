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
