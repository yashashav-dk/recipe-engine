"""Loads recipe and equipment YAML files into structured dicts."""

from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def load_recipe(path: Path) -> Dict[str, Any]:
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


def load_all_recipes(recipes_dir: Path) -> List[Dict[str, Any]]:
    """Load all .yaml files from the recipes directory."""
    recipes = []
    for path in sorted(recipes_dir.glob("*.yaml")):
        recipes.append(load_recipe(path))
    return recipes


def load_equipment(path: Path) -> Dict[str, Any]:
    """Load equipment.yaml. Returns dict with all equipment IDs for cross-referencing."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    all_ids: Set[str] = set()
    equipment_by_id: Dict[str, dict] = {}
    for category in ("appliances", "containers", "measuring"):
        for item in data.get(category, []):
            all_ids.add(item["id"])
            equipment_by_id[item["id"]] = item

    return {
        "raw": data,
        "all_ids": all_ids,
        "by_id": equipment_by_id,
    }
