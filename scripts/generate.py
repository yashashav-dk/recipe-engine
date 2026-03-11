"""Generates markdown docs and README from recipe YAML files."""

import argparse
import sys
from collections import defaultdict
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


def generate_readme(
    recipes,
    equipment_ids,
    equipment_by_id,
):
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
