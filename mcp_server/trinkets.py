"""
RDR2 Single-Player Trinkets & Talismans Metadata & Progress Formatter.
Tracks all 25 Trinkets & Talismans (6 Talismans, 13 Craftable Legendary Trinkets,
and 6 World/Quest Trinkets) plus 9 rare Talisman crafting ingredients.
"""

from typing import Dict, Any, List, Optional


TRINKETS_CATALOG: Dict[str, Dict[str, Any]] = {
    # --- 6 Talismans ---
    "alligator_tooth_talisman": {
        "name": "Alligator Tooth Talisman",
        "type": "talisman",
        "effect": "Permanently slows Dead Eye drain speed by 10%.",
        "source": "Craft at Fence (Legendary Bullgator Tooth + Gold Jointed Bracelet + Vintage Civil War Handcuffs). Unlocks Chapter 6.",
        "rare_ingredients": ["gold_jointed_bracelet", "vintage_civil_war_handcuffs"],
    },
    "bear_claw_talisman": {
        "name": "Bear Claw Talisman",
        "type": "talisman",
        "effect": "Permanently slows Health Core drain speed by 10%.",
        "source": "Craft at Fence (Legendary Bear Claw + Silver Chain Bracelet + Quartz Chunk).",
        "rare_ingredients": ["silver_chain_bracelet", "quartz_chunk"],
    },
    "bison_horn_talisman": {
        "name": "Bison Horn Talisman",
        "type": "talisman",
        "effect": "Permanently slows Stamina Core drain speed by 10%.",
        "source": "Craft at Fence (Legendary White Bison Horn + Abalone Shell Fragment + Silver Earring).",
        "rare_ingredients": ["abalone_shell_fragment", "silver_earring"],
    },
    "boar_tusk_talisman": {
        "name": "Boar Tusk Talisman",
        "type": "talisman",
        "effect": "Permanently slows Horse Health & Stamina Core drain speed by 10%.",
        "source": "Craft at Fence (Legendary Boar Tusk + Cobalt Petrified Wood + Gold Earring).",
        "rare_ingredients": ["cobalt_petrified_wood", "gold_earring"],
    },
    "raven_claw_talisman": {
        "name": "Raven Claw Talisman",
        "type": "talisman",
        "effect": "Permanently slows all weapon degradation by 20%.",
        "source": "Craft at Fence (Old Brass Compass from Francis Sinclair's cabin after Geology for Beginners).",
        "rare_ingredients": ["old_brass_compass"],
    },
    "eagle_talon_talisman": {
        "name": "Eagle Talon Talisman",
        "type": "talisman",
        "effect": "Permanently increases Eagle Eye duration by 5 seconds.",
        "source": "Special / Ultimate Edition bonus (available in Wardrobe).",
        "rare_ingredients": [],
    },
    # --- 13 Craftable Legendary Animal Trinkets ---
    "beaver_tooth_trinket": {
        "name": "Beaver Tooth Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently slows weapon degradation by 10%.",
        "source": "Craft at Fence (Legendary Beaver Tooth — Southwest of Butcher Creek).",
        "rare_ingredients": [],
    },
    "buck_antler_trinket": {
        "name": "Buck Antler Trinket",
        "type": "trinket_craftable",
        "effect": "Higher chance of higher-quality pelts when skinning animals.",
        "source": "Craft at Fence (Legendary Buck Antler — Northwest of Strawberry, Big Valley).",
        "rare_ingredients": [],
    },
    "cougar_fang_trinket": {
        "name": "Cougar Fang Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases Stamina XP bonus by 10%.",
        "source": "Craft at Fence (Legendary Cougar Fang — Gaptooth Ridge, Epilogue).",
        "rare_ingredients": [],
    },
    "coyote_fang_trinket": {
        "name": "Coyote Fang Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases Dead Eye XP bonus by 10%.",
        "source": "Craft at Fence (Legendary Coyote Fang — Scarlett Meadows, northwest of Rhodes).",
        "rare_ingredients": [],
    },
    "elk_antler_trinket": {
        "name": "Elk Antler Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases money received from looting by 10%.",
        "source": "Craft at Fence (Legendary Elk Antler — East of Bacchus Station, Grizzlies East).",
        "rare_ingredients": [],
    },
    "fox_claw_trinket": {
        "name": "Fox Claw Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases Eagle Eye duration by 5 seconds.",
        "source": "Craft at Fence (Legendary Fox Claw — Mattock Pond, north of Rhodes).",
        "rare_ingredients": [],
    },
    "lion_paw_trinket": {
        "name": "Lion's Paw Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases Stamina XP bonus by 10%.",
        "source": "Craft at Fence (Lion's Paw — Stranger Mission 'He's British, of Course' in Chapter 3+).",
        "rare_ingredients": [],
    },
    "moose_antler_trinket": {
        "name": "Moose Antler Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently increases Health XP bonus by 10%.",
        "source": "Craft at Fence (Legendary Moose Antler — Northeast Roanoke Ridge).",
        "rare_ingredients": [],
    },
    "panther_eye_trinket": {
        "name": "Panther's Eye Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently decreases Dead Eye drain speed by 10% for 3 seconds.",
        "source": "Craft at Fence (Legendary Panther Eye — Master Hunter Rank 10, Bolger Glade).",
        "rare_ingredients": [],
    },
    "pronghorn_horn_trinket": {
        "name": "Pronghorn Horn Trinket",
        "type": "trinket_craftable",
        "effect": "Animals stowed on horseback never spoil.",
        "source": "Craft at Fence (Legendary Pronghorn Horn — Rio Del Lobo Rock, Epilogue).",
        "rare_ingredients": [],
    },
    "ram_horn_trinket": {
        "name": "Ram Horn Trinket",
        "type": "trinket_craftable",
        "effect": "Doubles the amount of Creeping Thyme, Oregano, and Wild Mint picked.",
        "source": "Craft at Fence (Legendary Ram Horn — Cattail Pond, west of Valentine).",
        "rare_ingredients": [],
    },
    "tatanka_bison_horn_trinket": {
        "name": "Tatanka Bison Horn Trinket",
        "type": "trinket_craftable",
        "effect": "Permanently reduces melee damage taken by 10%.",
        "source": "Craft at Fence (Legendary Tatanka Bison Horn — Hennigan's Stead, Epilogue).",
        "rare_ingredients": [],
    },
    "wolf_heart_trinket": {
        "name": "Wolf Heart Trinket",
        "type": "trinket_craftable",
        "effect": "Doubles the amount of alcohol required to negatively affect the player.",
        "source": "Craft at Fence (Legendary Wolf Heart — Cotorra Springs, Ambarino).",
        "rare_ingredients": [],
    },
    # --- 6 World-Found / Quest Trinkets ---
    "cat_eye_trinket": {
        "name": "Cat Eye Trinket",
        "type": "trinket_world",
        "effect": "Permanently increases duration of fortifying tonic effects by 20%.",
        "source": "Lockbox on a small island in Flat Iron Lake (east of Braithwaite Manor / south of Rhodes).",
        "rare_ingredients": [],
    },
    "crow_beak_trinket": {
        "name": "Crow Beak Trinket",
        "type": "trinket_world",
        "effect": "Permanently increases looted ammo by 10%.",
        "source": "Final reward of the Elemental Trail Treasure Hunt (New Austin).",
        "rare_ingredients": [],
    },
    "hawk_talon_trinket": {
        "name": "Hawk Talon Trinket",
        "type": "trinket_world",
        "effect": "Permanently decreases Stamina drain speed by 30% when drawing a bow.",
        "source": "Lockbox in a rock crevice near the frozen waterfall at Deadboot Creek (Ambarino).",
        "rare_ingredients": [],
    },
    "owl_feather_trinket": {
        "name": "Owl Feather Trinket",
        "type": "trinket_world",
        "effect": "Permanently slows Health, Stamina, and Dead Eye Core drain by 15%.",
        "source": "Reward from Rains Fall during Chapter 6 mission 'Archeology for Beginners' (no killing).",
        "rare_ingredients": [],
    },
    "shark_tooth_trinket": {
        "name": "Shark Tooth Trinket",
        "type": "trinket_world",
        "effect": "Permanently increases Horse Bonding XP gain by 10%.",
        "source": "Lockbox next to a shipwreck on the northeastern coast above Annesburg (Roanoke Ridge).",
        "rare_ingredients": [],
    },
    "turtle_shell_trinket": {
        "name": "Turtle Shell Trinket",
        "type": "trinket_world",
        "effect": "Permanently increases Health bar regeneration speed by 10%.",
        "source": "Inside the Gaptooth Breach mine entrance (New Austin, Epilogue).",
        "rare_ingredients": [],
    },
}

INGREDIENT_LABELS: Dict[str, str] = {
    "silver_chain_bracelet": "Silver Chain Bracelet (Bear Claw Talisman)",
    "quartz_chunk": "Quartz Chunk (Bear Claw Talisman — Dinosaur Bones reward)",
    "gold_jointed_bracelet": "Gold Jointed Bracelet (Alligator Tooth Talisman)",
    "vintage_civil_war_handcuffs": "Vintage Civil War Handcuffs (Alligator Tooth Talisman — Cigarette Cards reward)",
    "abalone_shell_fragment": "Abalone Shell Fragment (Bison Horn Talisman — Rhodes abandoned house)",
    "silver_earring": "Silver Earring (Bison Horn Talisman)",
    "gold_earring": "Gold Earring (Boar Tusk Talisman)",
    "cobalt_petrified_wood": "Cobalt Petrified Wood (Boar Tusk Talisman — Lake Isabella chest)",
    "old_brass_compass": "Old Brass Compass (Raven Claw Talisman — Francis Sinclair cabin)",
}


def format_trinkets(
    raw_trinkets: Dict[str, Any],
    filter_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Enrich raw native trinket & talisman counts with bonuses, sources, and ingredient tracking."""
    owned_map = raw_trinkets.get("owned", {}) if isinstance(raw_trinkets, dict) else {}
    ing_map = raw_trinkets.get("ingredients", {}) if isinstance(raw_trinkets, dict) else {}

    mode = (filter_mode or "all").lower().strip()

    total_owned = 0
    total_possible = len(TRINKETS_CATALOG)
    active_bonuses: List[str] = []
    items_out: Dict[str, Any] = {}

    for key, meta in TRINKETS_CATALOG.items():
        qty = int(owned_map.get(key, 0))
        is_owned = qty > 0
        if is_owned:
            total_owned += 1
            active_bonuses.append(f"{meta['name']}: {meta['effect']}")

        if mode == "owned" and not is_owned:
            continue
        if mode == "missing" and is_owned:
            continue
        if mode == "talismans" and meta["type"] != "talisman":
            continue
        if mode == "trinkets" and meta["type"] == "talisman":
            continue

        entry: Dict[str, Any] = {
            "name": meta["name"],
            "type": meta["type"],
            "owned": is_owned,
            "effect": meta["effect"],
            "source": meta["source"],
        }

        if meta["rare_ingredients"] and not is_owned:
            entry["rare_ingredients_status"] = {
                ing: {
                    "label": INGREDIENT_LABELS.get(ing, ing),
                    "owned_count": int(ing_map.get(ing, 0)),
                    "have_it": int(ing_map.get(ing, 0)) > 0,
                }
                for ing in meta["rare_ingredients"]
            }

        items_out[key] = entry

    rare_in_satchel = {
        ing: {
            "label": INGREDIENT_LABELS.get(ing, ing),
            "count": int(ing_map.get(ing, 0)),
        }
        for ing in INGREDIENT_LABELS
        if int(ing_map.get(ing, 0)) > 0
    }

    return {
        "total_owned": total_owned,
        "total_possible": total_possible,
        "percent_complete": round((total_owned / total_possible) * 100.0, 1) if total_possible else 0.0,
        "active_bonuses": active_bonuses,
        "rare_ingredients_in_satchel": rare_in_satchel,
        "items": items_out,
    }
