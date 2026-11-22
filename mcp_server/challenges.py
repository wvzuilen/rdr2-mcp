"""
RDR2 Single-Player Challenges Metadata & Progress Formatter.
Covers all 9 challenge categories (90 ranks total) and maps raw native goal IDs
from RDR2_MCP_Bridge.asi into human-readable objectives, targets, and sub-goals.
"""

from typing import Dict, Any, List, Optional


CHALLENGE_CATALOG: Dict[str, Dict[str, Any]] = {
    "bandit": {
        "name": "Bandit",
        "reward_stat": "Stamina",
        "ranks": {
            1:  {"objective": "Hold up 5 townsfolk.", "target": 5},
            2:  {"objective": "Rob any 2 coaches or return any 2 stolen coaches to the Fence.", "target": 2},
            3:  {"objective": "Rob the cash register in any 4 shops in one day.", "target": 4},
            4:  {"objective": "Rob any 3 coaches or return any 3 stolen coaches to the Fence in one day.", "target": 3},
            5:  {"objective": "Amass a $250 bounty in one state.", "target": 250},
            6:  {"objective": "Steal 5 horses and sell them to the Horse Fence at Clemens Cove.", "target": 5},
            7:  {"objective": "Rob $50 worth of cash and valuables from townsfolk and travelers.", "target": 50},
            8:  {"objective": "Steal 7 wagons and sell them to the Fence at Emerald Ranch.", "target": 7},
            9:  {"objective": "Hogtie someone and leave them on the railroad 3 times.", "target": 3},
            10: {"objective": "Complete 5 train robberies without dying or being caught.", "target": 5},
        },
    },
    "explorer": {
        "name": "Explorer",
        "reward_stat": "Dead Eye",
        "ranks": {
            1:  {"objective": "Find a treasure map.", "target": 1},
            2:  {"objective": "Find a treasure.", "target": 1},
            3:  {"objective": "Find a treasure.", "target": 1},
            4:  {"objective": "Find a treasure.", "target": 1},
            5:  {"objective": "Find a treasure.", "target": 1},
            6:  {"objective": "Find a treasure.", "target": 1},
            7:  {"objective": "Find a treasure.", "target": 1},
            8:  {"objective": "Find a treasure.", "target": 1},
            9:  {"objective": "Find a treasure.", "target": 1},
            10: {"objective": "Find a treasure.", "target": 1},
        },
    },
    "gambler": {
        "name": "Gambler",
        "reward_stat": "Stamina",
        "ranks": {
            1:  {"objective": "Win 5 hands of Poker.", "target": 5},
            2:  {"objective": "In Blackjack, double down and win the hand 5 times.", "target": 5},
            3:  {"objective": "Win 3 games of Five Finger Fillet.", "target": 3},
            4:  {"objective": "Bust one Poker location out in each location (Flatneck Station, Saint Denis, Valentine).", "target": 3},
            5:  {"objective": "Win 3 rounds of Dominoes without drawing any tiles against 2 or fewer opponents.", "target": 3},
            6:  {"objective": "Beat the Blackjack dealer in two locations (Rhodes and Van Horn).", "target": 2},
            7:  {"objective": "Beat the Five Finger Fillet player in every location (Strawberry, Valentine, Van Horn).", "target": 3},
            8:  {"objective": "Win 3 hands of Blackjack with 3 hits or more.", "target": 3},
            9:  {"objective": "Win 3 games of Dominoes in a row.", "target": 3},
            10: {"objective": "Win 3 hands of Poker in a row.", "target": 3},
        },
    },
    "herbalist": {
        "name": "Herbalist",
        "reward_stat": "Dead Eye",
        "ranks": {
            1:  {"objective": "Pick 6 Yarrow.", "target": 6},
            2:  {"objective": "Pick and eat 4 species of berry.", "target": 4},
            3:  {"objective": "Craft 7 items using Sage as an ingredient.", "target": 7},
            4:  {"objective": "Pick 5 mushrooms and feed them to your horse.", "target": 5},
            5:  {"objective": "Craft 9 items using Indian Tobacco as an ingredient.", "target": 9},
            6:  {"objective": "Pick 15 different species of herb.", "target": 15},
            7:  {"objective": "Craft and use 5 Special Miracle Tonics.", "target": 5},
            8:  {"objective": "Use Oleander to craft 6 poison weapons.", "target": 6},
            9:  {"objective": "Pick one of each species of herb (43 total).", "target": 43},
            10: {"objective": "Season and cook all 11 types of meat.", "target": 11},
        },
    },
    "horseman": {
        "name": "Horseman",
        "reward_stat": "Stamina",
        "ranks": {
            1:  {"objective": "Kill 5 rabbits from horseback.", "target": 5},
            2:  {"objective": "Jump over 3 obstacles in 15 seconds.", "target": 3},
            3:  {"objective": "Ride from Valentine to Rhodes in less than 5 minutes.", "target": 1},
            4:  {"objective": "While mounted, drag a victim for 3,300 feet using your lasso.", "target": 3300},
            5:  {"objective": "Trample 5 animals while on horseback.", "target": 5},
            6:  {"objective": "Ride from Strawberry to Saint Denis in less than 9 minutes without touching any water.", "target": 1},
            7:  {"objective": "Kill 7 enemies from horseback without dismounting.", "target": 7},
            8:  {"objective": "Kill 9 predators from horseback.", "target": 9},
            9:  {"objective": "Ride from Van Horn to Blackwater in less than 17 minutes without touching any water.", "target": 1},
            10: {"objective": "Break every wild horse breed (9 breeds).", "target": 9},
        },
    },
    "master_hunter": {
        "name": "Master Hunter",
        "reward_stat": "Health",
        "ranks": {
            1:  {"objective": "Skin 3 deer.", "target": 3},
            2:  {"objective": "Collect 3 Perfect-quality rabbit pelts.", "target": 3},
            3:  {"objective": "Track 10 different animal species using your binoculars.", "target": 10},
            4:  {"objective": "Get a clean kill after calling to an animal 5 times.", "target": 5},
            5:  {"objective": "Skin 3 black or grizzly bears.", "target": 3},
            6:  {"objective": "Kill 5 cougars with your bow, and then skin them.", "target": 5},
            7:  {"objective": "Use bait to lure and kill both a herbivore and a predator.", "target": 2},
            8:  {"objective": "Catch 3 fish without using a fishing rod.", "target": 3},
            9:  {"objective": "Catch an opossum playing possum.", "target": 1},
            10: {"objective": "Find and kill the Legendary Panther, 'Giaguaro'.", "target": 1},
        },
    },
    "sharpshooter": {
        "name": "Sharpshooter",
        "reward_stat": "Health",
        "ranks": {
            1:  {"objective": "Kill 3 flying birds.", "target": 3},
            2:  {"objective": "Kill 2 different species of animal in the same Dead Eye use.", "target": 2},
            3:  {"objective": "Kill 5 flying birds while on a moving train.", "target": 5},
            4:  {"objective": "Kill an enemy at least 80 feet away with a thrown Tomahawk.", "target": 1},
            5:  {"objective": "Kill 6 animals without switching or reloading your weapon.", "target": 6},
            6:  {"objective": "Kill someone at least 660 feet away with a long scoped rifle.", "target": 1},
            7:  {"objective": "Get 7 headshots in a row.", "target": 7},
            8:  {"objective": "Disarm 3 enemies without reloading or switching your weapon.", "target": 3},
            9:  {"objective": "Shoot 3 people's hats off in the same Dead Eye use.", "target": 3},
            10: {"objective": "Kill 3 flying birds with 3 consecutive long scoped rifle shots.", "target": 3},
        },
    },
    "survivalist": {
        "name": "Survivalist",
        "reward_stat": "Dead Eye",
        "ranks": {
            1:  {"objective": "Catch 3 Bluegill fish.", "target": 3},
            2:  {"objective": "Hand 5 animals in to Pearson at camp or to the Trapper.", "target": 5},
            3:  {"objective": "Kill 5 animals using the Varmint Rifle.", "target": 5},
            4:  {"objective": "Craft a Dynamite, Fire, Improved, Poison, and Small Game Arrow.", "target": 5},
            5:  {"objective": "Catch a fish in the Bayou from a riverboat and while standing on railroad tracks.", "target": 2},
            6:  {"objective": "Kill a scavenging animal while it is feeding on a corpse 5 times.", "target": 5},
            7:  {"objective": "Kill 8 small game animals with consecutive shots, using Small Game Arrows.", "target": 8},
            8:  {"objective": "Craft a Homing Tomahawk, Improved Tomahawk, Volatile Fire Bottle, and Volatile Dynamite.", "target": 4},
            9:  {"objective": "Catch a fish that weighs at least 19 lbs.", "target": 1},
            10: {"objective": "Catch one of each type of fish throughout the world (15 species).", "target": 15},
        },
    },
    "weapons_expert": {
        "name": "Weapons Expert",
        "reward_stat": "Health",
        "ranks": {
            1:  {"objective": "Kill 3 enemies with a knife.", "target": 3},
            2:  {"objective": "Kill 3 enemies in 10 seconds using only throwing knives.", "target": 3},
            3:  {"objective": "Kill 3 birds of prey using only a Tomahawk.", "target": 3},
            4:  {"objective": "Kill 10 enemies with a shotgun using crafted ammo.", "target": 10},
            5:  {"objective": "Kill 5 mounted enemies, using 1 throwing knife per kill.", "target": 5},
            6:  {"objective": "Kill 4 enemies at the same time with a single stick of dynamite.", "target": 1},
            7:  {"objective": "Kill 4 consecutive enemies by throwing and retrieving the same Tomahawk.", "target": 4},
            8:  {"objective": "Kill 15 enemies using a long-barreled sidearm.", "target": 15},
            9:  {"objective": "Kill 9 unaware enemies from behind using the bow.", "target": 9},
            10: {"objective": "Kill a grizzly bear without taking damage, using only throwing knives.", "target": 1},
        },
    },
}

SUBGOAL_LABELS: Dict[str, str] = {
    # Gambler 4, 6, 7
    "ACW_GAMB_RANK_04_POKER_FNS": "Flatneck Station Poker",
    "ACW_GAMB_RANK_04_POKER_SDN": "Saint Denis Poker",
    "ACW_GAMB_RANK_04_POKER_VAL": "Valentine Poker",
    "ACW_GAMB_RANK_06_BLACKJACK_RHO": "Rhodes Blackjack",
    "ACW_GAMB_RANK_06_BLACKJACK_VAN": "Van Horn Blackjack",
    "ACW_GAMB_RANK_07_FIVEFINGER_STR": "Strawberry Five Finger Fillet",
    "ACW_GAMB_RANK_07_FIVEFINGER_VAL": "Valentine Five Finger Fillet",
    "ACW_GAMB_RANK_07_FIVEFINGER_VAN": "Van Horn Five Finger Fillet",
    # Herbalist 4, 7, 10
    "ACW_HERB_RANK_04_FEEDMUSHROOMS": "Feed 5 mushrooms to horse",
    "ACW_HERB_RANK_04_POTENTHERBIVOREBAIT": "Potent Herbivore Bait",
    "ACW_HERB_RANK_07_CRAFTSPECIALTONIC": "Craft 5 Special Miracle Tonics",
    "ACW_HERB_RANK_07_USESPECIALTONIC": "Use 5 Special Miracle Tonics",
    "ACW_HERB_RANK_10_BIGGAMEMEATSEASONING": "Big Game Meat",
    "ACW_HERB_RANK_10_CRUSTACEANMEATSEASONING": "Crustacean Meat",
    "ACW_HERB_RANK_10_EXOTICBIRDSEASONING": "Exotic Bird Meat",
    "ACW_HERB_RANK_10_FLAKEYFISHSEASONING": "Flaky Fish Meat",
    "ACW_HERB_RANK_10_GAMEMEATSEASONING": "Game Meat",
    "ACW_HERB_RANK_10_GRISTLYMUTTONSEASONING": "Gristly Mutton",
    "ACW_HERB_RANK_10_MATUREVENISONSEASONING": "Mature Venison",
    "ACW_HERB_RANK_10_PLUMPBIRDSEASONING": "Plump Bird Meat",
    "ACW_HERB_RANK_10_PRIMEBEEFSEASONING": "Prime Beef Joint",
    "ACW_HERB_RANK_10_SUCCULENTFISHSEASONING": "Succulent Fish Meat",
    "ACW_HERB_RANK_10_TENDERPORKSEASONING": "Tender Pork Loin",
    # Horseman 10
    "ACW_HORSE_RANK_10_AMERICAN_PAINT": "American Paint",
    "ACW_HORSE_RANK_10_AMERICAN_STANDARDBRED": "American Standardbred",
    "ACW_HORSE_RANK_10_APPALOOSA": "Appaloosa",
    "ACW_HORSE_RANK_10_ARABIAN": "Arabian",
    "ACW_HORSE_RANK_10_HUNGARIAN": "Hungarian Halfbred",
    "ACW_HORSE_RANK_10_KENTUCKY": "Kentucky Saddler",
    "ACW_HORSE_RANK_10_MORGAN": "Morgan",
    "ACW_HORSE_RANK_10_MUSTANG": "Mustang",
    "ACW_HORSE_RANK_10_NOKOTA": "Nokota",
    "ACW_HORSE_RANK_10_TENNESSEE": "Tennessee Walker",
    # Master Hunter 6
    "ACW_HUNT_RANK_06_COUGARKILL": "Kill 5 cougars with bow",
    "ACW_HUNT_RANK_06_COUGARSKIN": "Skin 5 cougars",
    # Survivalist 4, 5, 8, 10
    "ACW_SURV_RANK_04_DYNAMITEARROW": "Dynamite Arrow",
    "ACW_SURV_RANK_04_FIREARROW": "Fire Arrow",
    "ACW_SURV_RANK_04_IMPROVEDARROW": "Improved Arrow",
    "ACW_SURV_RANK_04_POISONARROW": "Poison Arrow",
    "ACW_SURV_RANK_04_SMALLGAMEARROW": "Small Game Arrow",
    "ACW_SURV_RANK_05_FISHINGRIVERBOAT": "Fish from riverboat in Bayou",
    "ACW_SURV_RANK_05_FISHINGTRACKS": "Fish from railroad tracks in Bayou",
    "ACW_SURV_RANK_08_HOMINGTOMAHAWK": "Homing Tomahawk",
    "ACW_SURV_RANK_08_IMPROVEDTOMAHAWK": "Improved Tomahawk",
    "ACW_SURV_RANK_08_VOLATILEDYNAMITE": "Volatile Dynamite",
    "ACW_SURV_RANK_08_VOLATILEFIREBOTTLE": "Volatile Fire Bottle",
    "ACW_SURV_RANK_10_BLUEGILL": "Bluegill",
    "ACW_SURV_RANK_10_BULLHEADCATFISH": "Bullhead Catfish",
    "ACW_SURV_RANK_10_CHAINPICKEREL": "Chain Pickerel",
    "ACW_SURV_RANK_10_CHANNELCATFISH": "Channel Catfish",
    "ACW_SURV_RANK_10_LAKESTURGEON": "Lake Sturgeon",
    "ACW_SURV_RANK_10_LARGEMOUTHBASS": "Largemouth Bass",
    "ACW_SURV_RANK_10_LONGNOSEGAR": "Longnose Gar",
    "ACW_SURV_RANK_10_MUSKIE": "Muskie",
    "ACW_SURV_RANK_10_NORTHERNPIKE": "Northern Pike",
    "ACW_SURV_RANK_10_PERCH": "Perch",
    "ACW_SURV_RANK_10_REDFINPICKEREL": "Redfin Pickerel",
    "ACW_SURV_RANK_10_ROCKBASS": "Rock Bass",
    "ACW_SURV_RANK_10_SMALLMOUTHBASS": "Smallmouth Bass",
    "ACW_SURV_RANK_10_SOCKEYESALMON": "Sockeye Salmon",
    "ACW_SURV_RANK_10_STEELHEADTROUT": "Steelhead Trout",
}


def format_challenges(
    raw_challenges: Dict[str, Any],
    category_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Enrich raw native challenge telemetry with human-readable objectives and summary stats."""
    total_completed = 0
    total_max = 0
    categories_completed: List[str] = []
    formatted: Dict[str, Any] = {}

    cat_filter = (category_filter or "all").lower().strip()

    for key, meta in CHALLENGE_CATALOG.items():
        raw = raw_challenges.get(key, {})
        completed = int(raw.get("ranks_completed", 0))
        max_ranks = int(raw.get("max_ranks", 10)) or 10
        is_done = completed >= max_ranks
        active_rank = None if is_done else (completed + 1)

        total_completed += completed
        total_max += max_ranks
        if is_done:
            categories_completed.append(meta["name"])

        if cat_filter not in ("", "all") and cat_filter != key:
            continue

        rank_info = meta["ranks"].get(active_rank, {}) if active_rank else {}
        next_info = meta["ranks"].get(active_rank + 1, {}) if (active_rank and active_rank < max_ranks) else {}

        raw_goals = raw.get("goals", [])
        goals_out = []
        for g in raw_goals:
            gid = g.get("id", "")
            goals_out.append({
                "id": gid,
                "label": SUBGOAL_LABELS.get(gid, rank_info.get("objective", gid)),
                "progress": int(g.get("progress", 0)),
                "complete": bool(g.get("complete", False)),
                "active": bool(g.get("active", False)),
            })

        entry: Dict[str, Any] = {
            "name": meta["name"],
            "reward_stat": meta["reward_stat"],
            "ranks_completed": completed,
            "max_ranks": max_ranks,
            "completed": is_done,
            "current_rank": active_rank,
            "current_objective": rank_info.get("objective") if active_rank else "All 10 ranks completed!",
        }

        if active_rank:
            target = rank_info.get("target")
            if target is not None:
                entry["target"] = target
            if len(goals_out) == 1:
                entry["progress"] = goals_out[0]["progress"]
                if target is not None:
                    entry["progress_text"] = f"{goals_out[0]['progress']} / {target}"
            elif len(goals_out) > 1:
                done_count = sum(1 for g in goals_out if g["complete"])
                entry["subgoals_completed"] = done_count
                entry["subgoals_total"] = len(goals_out)
                entry["subgoals"] = goals_out
            if next_info:
                entry["next_rank_objective"] = f"Rank {active_rank + 1}: {next_info['objective']}"

        formatted[key] = entry

    return {
        "total_ranks_completed": total_completed,
        "total_ranks_max": total_max,
        "percent_complete": round((total_completed / total_max) * 100.0, 1) if total_max else 0.0,
        "categories_completed": categories_completed,
        "challenges": formatted,
    }
