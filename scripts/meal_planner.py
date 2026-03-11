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
