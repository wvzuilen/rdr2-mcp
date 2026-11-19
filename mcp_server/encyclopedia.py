"""
RDR2 Encyclopedia & Knowledge Base
Provides structured offline lookup data for hunting, satchel crafting, camp upgrades, and trinkets.
"""

from typing import Dict, Any, List, Optional


LEGENDARY_ANIMALS: Dict[str, Dict[str, Any]] = {
    "bear": {
        "name": "Legendary Bharati Grizzly Bear",
        "location": "Grizzlies East, north of O'Creagh's Run",
        "weapon_recommendation": "Springfield Rifle / Rolling Block with Express Ammo, or High-Capacity Shotgun with Slugs",
        "pelt_uses": "Legendary Bear Head Hat, Bear Coat, Bear Ropers (Trapper)",
        "talisman_trinket": "Bear Claw Talisman",
        "effect": "Permanently decreases Health Core drain speed by 10%"
    },
    "buck": {
        "name": "Legendary Buck",
        "location": "Big Valley, northwest of Strawberry (Black Bone Forest / Mount Shann)",
        "weapon_recommendation": "Springfield Rifle or Bow with Improved Arrows (Clean headshot)",
        "pelt_uses": "Legendary Buck Vest, Fox & Buck Holster (Trapper)",
        "talisman_trinket": "Buck Antler Trinket",
        "effect": "Permanently improves quality of all skinned animals; increases chance of higher quality animal parts"
    },
    "coyote": {
        "name": "Legendary Coyote",
        "location": "The Heartlands, northwest of Rhodes (near Dewberry Creek)",
        "weapon_recommendation": "Varmint Rifle or Repeater",
        "pelt_uses": "Legendary Coyote Mountain Hat, Half Chaps (Trapper)",
        "talisman_trinket": "Coyote Fang Trinket",
        "effect": "Permanently increases Dead Eye experience gain by 10%"
    },
    "fox": {
        "name": "Legendary Fox",
        "location": "Mattock Pond, north of Rhodes",
        "weapon_recommendation": "Varmint Rifle or Bow",
        "pelt_uses": "Legendary Fox Moccasins (Trapper)",
        "talisman_trinket": "Fox Claw Trinket",
        "effect": "Permanently increases Eagle Eye duration by 5 seconds"
    },
    "bison_white": {
        "name": "Legendary White Bison",
        "location": "Lake Isabella, Grizzlies West (Ambarino)",
        "weapon_recommendation": "Springfield Rifle / Sniper Rifle with Express Ammo",
        "pelt_uses": "Legendary White Bison Hat, Coat (Trapper)",
        "talisman_trinket": "Bison Horn Talisman",
        "effect": "Permanently decreases Stamina Core drain speed by 10%"
    },
    "panther": {
        "name": "Legendary Giaguaro Panther",
        "location": "Bolger Glade, south of Rhodes (Requires Master Hunter Rank 9)",
        "weapon_recommendation": "Shotgun with Slugs or Springfield Rifle with Express Ammo (Fast Dead Eye reaction)",
        "pelt_uses": "Legendary Panther Cloak, Range Gloves (Trapper)",
        "talisman_trinket": "Panther's Eye Trinket",
        "effect": "Decreases the speed at which the Dead Eye bar drains by 10% for the first 3 seconds"
    }
}


SATCHEL_RECIPES: Dict[str, Dict[str, Any]] = {
    "tonics": {
        "name": "Tonics Satchel",
        "capacity": "Increases carrying capacity for all tonics to 99 (when combined) or 5 to 7",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Buck Pelt", "1x Perfect Elk Pelt"],
        "camp_requirement": "Leather Working Tools purchased from Ledger"
    },
    "ingredients": {
        "name": "Ingredients Satchel",
        "capacity": "Increases carrying capacity for all edible plants and crafting ingredients",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Badger Pelt", "1x Perfect Squirrel Pelt"],
        "camp_requirement": "Donate 5 carcasses to Pearson"
    },
    "kit": {
        "name": "Kit Satchel",
        "capacity": "Increases carrying capacity for all types of equipment and kits",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Elk Pelt", "1x Perfect Panther Pelt"],
        "camp_requirement": "Donate 3 valuables to the camp tithing box"
    },
    "provisions": {
        "name": "Provisions Satchel",
        "capacity": "Increases carrying capacity for all food items and provisions",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Bison Pelt", "1x Perfect Raccoon Pelt"],
        "camp_requirement": "Upgrade Pearson's Wagon twice"
    },
    "materials": {
        "name": "Materials Satchel",
        "capacity": "Increases carrying capacity for mostly non-edible plant and animal parts",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Boar Pelt", "1x Perfect Iguana Skin"],
        "camp_requirement": "Craft 3 recipes at the scout campfire"
    },
    "valuables": {
        "name": "Valuables Satchel",
        "capacity": "Increases carrying capacity for all valuables (watches, jewelry)",
        "requirements": ["1x Perfect Deer Pelt", "1x Perfect Beaver Pelt", "1x Perfect Rabbit Pelt"],
        "camp_requirement": "Donate $50 into the camp tithing box"
    },
    "legend_of_the_east": {
        "name": "Legend of the East Satchel (ULTIMATE)",
        "capacity": "MASSIVELY increases carrying capacity for EVERY item in the game to 99!",
        "requirements": [
            "Craft all 6 preceding satchels",
            "1x Perfect Deer Pelt",
            "1x Perfect Cougar Pelt",
            "1x Perfect Wolf Pelt"
        ],
        "camp_requirement": "All other 6 satchels crafted at Pearson"
    }
}


CAMP_UPGRADES: Dict[str, Dict[str, Any]] = {
    "leather_working_tools": {
        "name": "Leather Working Tools",
        "cost": "$225",
        "importance": "CRITICAL - Must buy first",
        "description": "Enables Pearson to craft all custom satchels, camp decorations, and equipment upgrades."
    },
    "dutch_lodging": {
        "name": "Lodging: First Things First (Dutch's Tent)",
        "cost": "$220",
        "importance": "HIGH",
        "description": "Encourages the rest of the camp to donate more money. Required to unlock Arthur's tent upgrade."
    },
    "arthur_lodging": {
        "name": "Lodging: Next in Line (Arthur's Tent & Fast Travel)",
        "cost": "$260",
        "importance": "CRITICAL",
        "description": "Unlocks the Fast Travel Map on Arthur's wagon and enables Fast Travel directly from any wilderness campfire."
    },
    "chicken_coop": {
        "name": "Chicken Coop",
        "cost": "$175",
        "importance": "MEDIUM",
        "description": "Adds eggs to camp stew, boosting Dead Eye cores whenever eating at camp."
    },
    "horse_station": {
        "name": "Horse Station",
        "cost": "$300",
        "importance": "LOW",
        "description": "Allows retrieving any stabled horse directly from camp without riding to a town stable."
    }
}


HUNTING_TIERS: Dict[str, Dict[str, Any]] = {
    "small": {
        "animals": ["Squirrel", "Toad", "Frog", "Small Bird (Robin, Cardinal, Bluejay, Songbird)", "Snake", "Bat", "Rat"],
        "weapon": "Bow with Small Game Arrows",
        "note": "Any bullet or normal arrow will instantly degrade the carcass to 1 star!"
    },
    "moderate": {
        "animals": ["Rabbit", "Badger", "Muskrat", "Raccoon", "Beaver", "Skunk", "Possum", "Iguana", "Eagle", "Hawk"],
        "weapon": "Varmint Rifle (.22 caliber)",
        "note": "Aim for headshot with .22 caliber. Do not use repeaters or revolvers."
    },
    "medium": {
        "animals": ["Coyote", "Fox", "Pig", "Beaver", "Goat"],
        "weapon": "Repeater, Bow with Regular Arrow, or Rifle (Headshot)"
    },
    "large": {
        "animals": ["Deer", "Buck", "Pronghorn", "Ram", "Wolf", "Boar", "Cougar", "Panther"],
        "weapon": "Rifle (Springfield or Bolt Action) or Bow with Regular/Poison Arrow",
        "note": "Clean single headshot required for 3-star Perfect Pelt."
    },
    "massive": {
        "animals": ["Bear (Grizzly / Black)", "Bison", "Elk", "Moose", "Alligator", "Bull", "Ox"],
        "weapon": "Rifle (Springfield or Bolt Action) with Express/High Velocity Ammo, or Improved Arrow",
        "note": "Aim for brain/heart or single sniper headshot."
    }
}


def query_encyclopedia(category: str, query: str = "") -> Dict[str, Any]:
    """Search the offline RDR2 knowledge base."""
    category = category.lower().strip()
    query = query.lower().strip()

    if category in ["satchel", "satchels"]:
        if query:
            for k, v in SATCHEL_RECIPES.items():
                if query in k or query in v["name"].lower():
                    return {"result": v}
        return {"satchels": SATCHEL_RECIPES}

    elif category in ["legendary", "animal", "animals", "trinket", "talisman"]:
        if query:
            for k, v in LEGENDARY_ANIMALS.items():
                if query in k or query in v["name"].lower():
                    return {"result": v}
        return {"legendary_animals": LEGENDARY_ANIMALS}

    elif category in ["camp", "ledger", "upgrade", "upgrades"]:
        if query:
            for k, v in CAMP_UPGRADES.items():
                if query in k or query in v["name"].lower():
                    return {"result": v}
        return {"camp_upgrades": CAMP_UPGRADES}

    elif category in ["hunting", "weapons", "pelts", "tiers"]:
        if query:
            for k, v in HUNTING_TIERS.items():
                if query in k or any(query in a.lower() for a in v["animals"]):
                    return {"result": v}
        return {"hunting_tiers": HUNTING_TIERS}

    return {
        "error": f"Unknown category '{category}'. Available categories: 'satchels', 'animals', 'camp', 'hunting'."
    }
