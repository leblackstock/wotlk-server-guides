import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED = json.loads((ROOT / "data" / "ah-crafted-sections.json").read_text(encoding="utf-8"))
RECIPES = json.loads((ROOT / "data" / "ah-enchanting-recipe-audit.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "data" / "ah-enchanting-price-evidence.json").read_text(encoding="utf-8"))
USE_AUDIT = json.loads((ROOT / "data" / "ah-profession-use-audit.json").read_text(encoding="utf-8"))
GUIDE = ROOT / "guides" / "enchanting-mats-ah-price-guide.html"
PRICE_BANDS = ("quick", "target", "high")


def merged_item(key):
    raw = CRAFTED["catalog"][key]
    return CRAFTED["catalog_defaults"] | CRAFTED["price_profiles"][raw["profile"]] | raw


def rows():
    return [
        (section, key, merged_item(key))
        for section in CRAFTED["guides"]["enchanting-mats-ah-price-guide.html"]["sections"]
        for key in section["items"]
    ]


def test_enchanting_evidence_inventory_and_rules():
    catalog_rows = rows()
    assert len(catalog_rows) == 276
    assert len({item["item_id"] for _, _, item in catalog_rows}) == 276
    assert EVIDENCE["method"] == "Evidence Pricing"
    assert EVIDENCE["model_version"] == "enchanting-evidence-pricing-v1"
    assert len(EVIDENCE["items"]) == 276
    assert EVIDENCE["rules"]["active_hellscream_listing_prices_used"] is False
    assert EVIDENCE["rules"]["external_gold_values_copied"] is False
    assert EVIDENCE["summary"]["external_gold_values_copied"] is False
    assert EVIDENCE["summary"]["scrolls_reviewed"] == 259
    assert EVIDENCE["summary"]["oils_reviewed"] == 9
    assert EVIDENCE["summary"]["wands_reviewed"] == 4
    assert EVIDENCE["summary"]["intermediates_gems_reviewed"] == 4


def test_every_output_has_exact_recipe_and_reviewed_band():
    assert len(RECIPES["recipes"]) == 276
    assert RECIPES["pricing_policy"]["active_hellscream_listings_used"] is False
    scroll_count = 0
    other_count = 0
    for _, key, item in rows():
        record = EVIDENCE["items"][str(item["item_id"])]
        recipe = RECIPES["recipes"][key]
        assert record["canonical_key"] == key
        assert record["recipe"]["source_spell_id"] == item["source_spell_id"]
        assert record["reagent_floor"] == item["pricing_floor_copper"]
        proposed = record["proposal"]["proposed_band"]
        assert proposed["quick"] <= proposed["target"] <= proposed["high"]
        assert {band: item[f"{band}_copper"] for band in PRICE_BANDS} == proposed
        assert item["price_strategy"] == "evidence-pricing-market-value"
        expected_ref = (
            "data/ah-gathering-material-price-evidence.json#items/12655"
            if item["item_id"] == 12655
            else f"data/ah-enchanting-price-evidence.json#items/{item['item_id']}"
        )
        assert item["price_evidence_ref"] == expected_ref
        if recipe["pricing_rule"] == "enchant-scroll-plus-vellum":
            scroll_count += 1
            assert recipe["vellum"]["rank"] == item["vellum_rank"]
            assert recipe["vellum"]["kind"] in {"armor", "weapon"}
        else:
            other_count += 1
            assert "vellum" not in recipe
    assert (scroll_count, other_count) == (259, 17)


def test_vellum_recipes_and_known_rank_boundaries():
    assert {
        key: record["output_count"] for key, record in RECIPES["vellum_recipes"].items()
    } == {
        "armor-1": 2,
        "armor-2": 2,
        "armor-3": 2,
        "weapon-1": 2,
        "weapon-2": 2,
        "weapon-3": 2,
    }
    assert merged_item("ench-scroll-of-enchant-gloves-angler")["vellum_rank"] == 1
    assert merged_item("ench-scroll-of-enchant-weapon-mongoose")["vellum_rank"] == 2
    assert merged_item("ench-scroll-of-enchant-weapon-berserking")["vellum_rank"] == 3


def test_large_changes_and_external_observations_are_safeguarded():
    large = [
        record for record in EVIDENCE["items"].values()
        if record["proposal"]["requires_large_change_review"]
    ]
    assert len(large) == EVIDENCE["summary"]["target_changes_over_fifty_percent"]
    assert all(record["proposal"]["reviewer_decision"] in {"accept", "retain", "revise"} for record in large)
    for record in EVIDENCE["items"].values():
        assert record["external_relative_review"]["used_to_set_gold_value"] is False
        for observation in record["source_observations"].values():
            assert "median_buyout_copper" not in observation
            assert "economy_scale" not in observation


def test_finished_outputs_have_no_hard_profession_requirement():
    restricted = {
        int(record["item_id"])
        for record in USE_AUDIT["canonical_hard_requirements"].values()
    }
    audience = {
        int(record["item_id"])
        for record in USE_AUDIT["canonical_profession_audience"].values()
    }
    output_ids = {int(item["item_id"]) for _, _, item in rows()}
    assert not output_ids & restricted
    assert not output_ids & audience


def test_sections_are_target_sorted_and_notes_are_specific():
    for section in CRAFTED["guides"]["enchanting-mats-ah-price-guide.html"]["sections"]:
        items = [merged_item(key) for key in section["items"]]
        expected = sorted(items, key=lambda item: (-item["target_copper"], item["name"].casefold()))
        assert [item["item_id"] for item in items] == [item["item_id"] for item in expected]
        assert all(item["row_note"].strip() for item in items)
        assert all("Reagent floor:" not in item["row_note"] for item in items)
    wrath = {item["name"]: item["row_note"] for section, _, item in rows() if "Crafted Wrath" in section["title"]}
    assert "spell power by 81" in wrath["Scroll of Enchant Staff - Greater Spellpower"]
    assert "attack power by 400" in wrath["Scroll of Enchant Weapon - Berserking"]
    assert "movement speed" in wrath["Scroll of Enchant Boots - Tuskarr's Vitality"]
    assert "resilience rating by 20" in wrath["Scroll of Enchant Chest - Exceptional Resilience"]


def test_rendered_guide_has_one_shared_note_and_all_recipe_links():
    source = GUIDE.read_text(encoding="utf-8")
    assert source.count('id="crafted-enchanting-pricing-note"') == 1
    assert source.count("Evidence Pricing and craft diagnostics") == 277
    assert source.count('class="crafted-recipe-link ') == 276
    assert "Reagent floor and pricing" not in source
    assert "Updated 2026-08-08" in source


if __name__ == "__main__":
    test_enchanting_evidence_inventory_and_rules()
    test_every_output_has_exact_recipe_and_reviewed_band()
    test_vellum_recipes_and_known_rank_boundaries()
    test_large_changes_and_external_observations_are_safeguarded()
    test_finished_outputs_have_no_hard_profession_requirement()
    test_sections_are_target_sorted_and_notes_are_specific()
    test_rendered_guide_has_one_shared_note_and_all_recipe_links()
    print(
        "Validated all 276 Enchanting Evidence Pricing decisions, exact recipes "
        "and vellums, profession use, notes, ordering, and rendered recipe links."
    )
