"""Generates markdown docs and README from recipe YAML files."""

import argparse
from pathlib import Path

from loader import load_all_recipes, load_equipment


def recipe_to_markdown(recipe: dict) -> str:
    """Convert a recipe dict to a markdown string. Omits sections for missing fields."""
    lines = [f"# {recipe['name']}", ""]

    # Status always shown
    lines.append(f"**Status:** {recipe['status']}")

    # Optional metadata
    if recipe["cuisine"]:
        lines.append(f"**Cuisine:** {recipe['cuisine']}")
    if recipe["category"]:
        lines.append(f"**Category:** {recipe['category']}")
    if recipe["servings"] is not None:
        lines.append(f"**Servings:** {recipe['servings']}")
    if recipe["prep_time_mins"] is not None:
        lines.append(f"**Prep:** {recipe['prep_time_mins']} mins")
    if recipe["cook_time_mins"] is not None:
        lines.append(f"**Cook:** {recipe['cook_time_mins']} mins")
    if recipe["cost_per_serving_usd"] is not None:
        lines.append(f"**Cost/serving:** ${recipe['cost_per_serving_usd']:.2f}")

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
