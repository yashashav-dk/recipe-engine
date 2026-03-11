import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from loader import load_recipe


def test_load_recipe_full(tmp_path):
    recipe_file = tmp_path / "chicken-tikka.yaml"
    recipe_file.write_text(
        "name: Chicken Tikka\n"
        "status: tested\n"
        "cuisine: Indian\n"
        "category: protein\n"
        "servings: 8\n"
        "prep_time_mins: 15\n"
        "cook_time_mins: 25\n"
        "equipment:\n"
        "  - instant-pot\n"
        "cost_per_serving_usd: 1.50\n"
        "tags:\n"
        "  - high-protein\n"
        "ingredients:\n"
        "  - item: chicken thighs\n"
        "    qty: 900\n"
        "    unit: g\n"
    )
    recipe = load_recipe(recipe_file)
    assert recipe["name"] == "Chicken Tikka"
    assert recipe["status"] == "tested"
    assert recipe["servings"] == 8
    assert recipe["equipment"] == ["instant-pot"]
    assert recipe["ingredients"][0]["item"] == "chicken thighs"
    assert recipe["slug"] == "chicken-tikka"


def test_load_recipe_minimal(tmp_path):
    recipe_file = tmp_path / "quick-idea.yaml"
    recipe_file.write_text("name: Quick Idea\n")
    recipe = load_recipe(recipe_file)
    assert recipe["name"] == "Quick Idea"
    assert recipe["status"] == "draft"
    assert recipe["servings"] is None
    assert recipe["equipment"] == []
    assert recipe["ingredients"] == []
    assert recipe["tags"] == []
    assert recipe["slug"] == "quick-idea"


from loader import load_all_recipes, load_equipment


def test_load_all_recipes(tmp_path):
    (tmp_path / "aaa.yaml").write_text("name: AAA\n")
    (tmp_path / "bbb.yaml").write_text("name: BBB\nstatus: staple\n")
    (tmp_path / "not-yaml.txt").write_text("ignored")
    recipes = load_all_recipes(tmp_path)
    assert len(recipes) == 2
    assert recipes[0]["name"] == "AAA"
    assert recipes[1]["name"] == "BBB"


def test_load_equipment(tmp_path):
    equip_file = tmp_path / "equipment.yaml"
    equip_file.write_text(
        "appliances:\n"
        "  - id: instant-pot\n"
        "    name: Instant Pot Duo\n"
        "    size: 5.7L\n"
        "containers:\n"
        "  - id: glass-2l\n"
        "    name: 2L Glass Container\n"
        "    count: 2\n"
        "    capacity_liters: 2\n"
        "measuring:\n"
        "  - id: cup-250ml\n"
        "    name: 250ml Cup\n"
    )
    equip = load_equipment(equip_file)
    assert "instant-pot" in equip["all_ids"]
    assert "glass-2l" in equip["all_ids"]
    assert "cup-250ml" in equip["all_ids"]
    assert equip["by_id"]["instant-pot"]["name"] == "Instant Pot Duo"
