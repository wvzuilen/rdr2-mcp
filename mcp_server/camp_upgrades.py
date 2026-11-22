"""
RDR2 Single-Player Camp Ledger Upgrades Metadata & Progress Formatter.
Maps live Global_40.f_4283.f_313..f_322 upgrade levels from RDR2_MCP_Bridge.asi
into structured tier names, prices, prerequisites, and unlock summaries.
"""

from typing import Dict, Any, List, Optional


CAMP_UPGRADE_CATALOG: Dict[str, Dict[str, Any]] = {
    "lodging": {
        "name": "Lodging",
        "max_level": 3,
        "tiers": [
            {
                "level": 1,
                "name": "First Things First (Dutch's Tent)",
                "price": 220,
                "effect": "Improves Dutch's tent and motivates gang members to donate more to the camp box.",
            },
            {
                "level": 2,
                "name": "Next in Line (Arthur's Wagon & Fast Travel Map)",
                "price": 325,
                "effect": "Unlocks the Fast Travel Map at Arthur's wagon and at wilderness campfires.",
            },
            {
                "level": 3,
                "name": "All the Rest (Gang Lodging)",
                "price": 300,
                "effect": "Improves all gang members' tents and raises camp morale.",
            },
        ],
    },
    "provisions": {
        "name": "Provisions Wagon",
        "max_level": 3,
        "tiers": [
            {"level": 1, "name": "More Provisions", "price": 30, "effect": "Adds extra food rations at Pearson's wagon."},
            {"level": 2, "name": "Better Provisions", "price": 60, "effect": "Improves food quality and camp stock."},
            {"level": 3, "name": "Best Provisions", "price": 90, "effect": "Adds premium alcohol and top-tier provisions."},
        ],
    },
    "medicine": {
        "name": "Medicine Wagon",
        "max_level": 3,
        "tiers": [
            {"level": 1, "name": "More Medicine", "price": 30, "effect": "Adds basic health cures and tonics at Strauss' wagon."},
            {"level": 2, "name": "Better Medicine", "price": 50, "effect": "Adds bitters, snake oil, and stronger tonics."},
            {"level": 3, "name": "Best Medicine", "price": 75, "effect": "Adds Potent Health Cures, Horse Revivers, and Miracle Tonics."},
        ],
    },
    "munitions": {
        "name": "Munitions Wagon",
        "max_level": 3,
        "tiers": [
            {"level": 1, "name": "More Ammo", "price": 35, "effect": "Adds revolver, repeater, and shotgun ammo at Arthur's wagon."},
            {"level": 2, "name": "Better Ammo", "price": 60, "effect": "Adds rifle ammo, throwing knives, and fire bottles."},
            {"level": 3, "name": "Best Ammo", "price": 85, "effect": "Adds High Velocity ammo, arrows, and dynamite."},
        ],
    },
    "leather_working_tools": {
        "name": "Leather Working Tools",
        "max_level": 1,
        "tiers": [
            {
                "level": 1,
                "name": "Leather Working Tools",
                "price": 225,
                "effect": "Unlocks Pearson's satchel crafting (including Legend of the East Satchel) and camp cosmetics.",
            }
        ],
    },
    "horse_station": {
        "name": "Horse Station",
        "max_level": 1,
        "tiers": [
            {
                "level": 1,
                "name": "Horse Station",
                "price": 300,
                "effect": "Allows retrieving and switching stabled horses directly from camp.",
            }
        ],
    },
    "chicken_coop": {
        "name": "Chicken Coop",
        "max_level": 1,
        "tiers": [
            {
                "level": 1,
                "name": "Chicken Coop",
                "price": 175,
                "effect": "Permanently upgrades Pearson's camp stew to grant a Golden Dead Eye Core.",
            }
        ],
    },
    "boat": {
        "name": "Camp Boat",
        "max_level": 1,
        "tiers": [
            {
                "level": 1,
                "name": "Camp Rowboat",
                "price": 450,
                "effect": "Provides a docked rowboat at Clemens Point and Shady Belle (available starting in Chapter 3).",
            }
        ],
    },
}


def format_camp_upgrades(raw_camp: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich raw native camp upgrade levels with names, prices, and remaining cost."""
    total_purchased = 0
    total_possible = 0
    remaining_cost = 0
    formatted: Dict[str, Any] = {}

    for key, meta in CAMP_UPGRADE_CATALOG.items():
        raw_entry = raw_camp.get(key, {})
        max_lvl = meta["max_level"]
        level = int(raw_entry.get("level", 0))
        level = max(0, min(level, max_lvl))
        maxed = level >= max_lvl

        total_purchased += level
        total_possible += max_lvl

        purchased_tiers: List[str] = []
        next_tier: Optional[Dict[str, Any]] = None
        for t in meta["tiers"]:
            if t["level"] <= level:
                purchased_tiers.append(t["name"])
            else:
                remaining_cost += t["price"]
                if next_tier is None:
                    next_tier = t

        entry: Dict[str, Any] = {
            "name": meta["name"],
            "level": level,
            "max_level": max_lvl,
            "purchased": level > 0,
            "maxed": maxed,
            "purchased_tiers": purchased_tiers,
        }
        if next_tier:
            entry["next_tier"] = next_tier

        formatted[key] = entry

    lodging_lvl = formatted["lodging"]["level"]
    return {
        "available": bool(raw_camp.get("available", True)),
        "total_upgrades_purchased": total_purchased,
        "total_upgrades_possible": total_possible,
        "percent_complete": round((total_purchased / total_possible) * 100.0, 1) if total_possible else 0.0,
        "remaining_cost_dollars": remaining_cost,
        "fast_travel_unlocked": lodging_lvl >= 2,
        "leather_working_tools_unlocked": formatted["leather_working_tools"]["purchased"],
        "upgrades": formatted,
    }
