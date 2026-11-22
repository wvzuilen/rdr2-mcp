/**
 * RDR2_MCP_Bridge - Native In-Game ScriptHook Telemetry Bridge for RDR2
 * Exposes real-time game state over a local HTTP server at http://127.0.0.1:28999
 * Built with pure Win32 + C runtime (zero C++ stdlib DLL dependencies).
 */

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#pragma comment(lib, "ws2_32.lib")

typedef uint64_t UINT64;

struct NativeVec3 {
    float x;
    uint32_t _pad0;
    float y;
    uint32_t _pad1;
    float z;
    uint32_t _pad2;
};

// ScriptHookRDR2 dynamic exports
typedef void (*fn_scriptRegister_t)(HMODULE, void (*)());
typedef void (*fn_scriptUnregister_t)(HMODULE);
typedef void (*fn_scriptWait_t)(DWORD);
typedef void (*fn_nativeInit_t)(UINT64);
typedef void (*fn_nativePush64_t)(UINT64);
typedef UINT64* (*fn_nativeCall_t)();
typedef UINT64* (*fn_getGlobalPtr_t)(int);

static fn_scriptRegister_t   fn_scriptRegister   = nullptr;
static fn_scriptUnregister_t fn_scriptUnregister = nullptr;
static fn_scriptWait_t       fn_scriptWait       = nullptr;
static fn_scriptWait_t       fn_realScriptWait   = nullptr;
static fn_nativeInit_t       fn_nativeInit       = nullptr;
static fn_nativePush64_t     fn_nativePush64     = nullptr;
static fn_nativeCall_t       fn_nativeCall       = nullptr;
static fn_getGlobalPtr_t     fn_getGlobalPtr     = nullptr;

static HMODULE          g_hModule = nullptr;
static volatile LONG    g_running = 1;
static volatile LONG    g_scriptMainActive = 0;
static volatile LONG    g_inTick = 0;
static LONG             g_server_started = 0;
static LONG             g_cs_initialized = 0;
static CRITICAL_SECTION g_cs;
static SOCKET           g_listen_sock = INVALID_SOCKET;
static ULONGLONG        g_lastTickMs = 0;
static bool             g_scriptWaitHooked = false;
static uint8_t          g_origScriptWaitBytes[16] = {0};

extern "C" {
__declspec(dllexport) char g_json_buf[16384] = "{\"bridge\":\"initializing\",\"bridge_active\":true,\"in_game\":false}";

// Pending waypoint command from HTTP POST /waypoint or direct memory bridge
__declspec(dllexport) volatile LONG g_pending_wp = 0;
__declspec(dllexport) float g_wp_x = 0.0f;
__declspec(dllexport) float g_wp_y = 0.0f;
__declspec(dllexport) float g_wp_z = 0.0f;
}
static bool g_gps_route_active = false;
static int g_gps_refresh_ticks = 0;
static int g_chal_refresh_ticks = 0;

static const int SERVER_PORT = 28999;

// Lowercase Jenkins One-At-A-Time hash
static uint32_t joaat(const char* str) {
    uint32_t hash = 0;
    while (*str) {
        unsigned char c = (unsigned char)*str++;
        if (c >= 'A' && c <= 'Z') c += 32;
        hash += c;
        hash += (hash << 10);
        hash ^= (hash >> 6);
    }
    hash += (hash << 3);
    hash ^= (hash >> 11);
    hash += (hash << 15);
    return hash;
}

static inline UINT64 pack_float(float f) {
    UINT64 v = 0;
    memcpy(&v, &f, sizeof(float));
    return v;
}

static inline float unpack_float(UINT64 v) {
    float f = 0.0f;
    memcpy(&f, &v, sizeof(float));
    return f;
}

// ScriptHook native invocation helpers (must ONLY be called from ScriptMain fiber)
static int call_int_0(UINT64 hash) {
    fn_nativeInit(hash);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static uint32_t call_u32_0(UINT64 hash) {
    fn_nativeInit(hash);
    UINT64* r = fn_nativeCall();
    return r ? (uint32_t)r[0] : 0;
}

static int call_int_1(UINT64 hash, UINT64 a0) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static uint32_t call_u32_1(UINT64 hash, UINT64 a0) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    UINT64* r = fn_nativeCall();
    return r ? (uint32_t)r[0] : 0;
}

static int call_int_2(UINT64 hash, UINT64 a0, UINT64 a1) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    fn_nativePush64(a1);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static int call_int_3(UINT64 hash, UINT64 a0, UINT64 a1, UINT64 a2) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    fn_nativePush64(a1);
    fn_nativePush64(a2);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static int call_int_4(UINT64 hash, UINT64 a0, UINT64 a1, UINT64 a2, UINT64 a3) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    fn_nativePush64(a1);
    fn_nativePush64(a2);
    fn_nativePush64(a3);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static int call_int_5(UINT64 hash, UINT64 a0, UINT64 a1, UINT64 a2, UINT64 a3, UINT64 a4) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    fn_nativePush64(a1);
    fn_nativePush64(a2);
    fn_nativePush64(a3);
    fn_nativePush64(a4);
    UINT64* r = fn_nativeCall();
    return r ? (int)(int64_t)r[0] : 0;
}

static float call_float_1(UINT64 hash, UINT64 a0) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    UINT64* r = fn_nativeCall();
    return r ? unpack_float(r[0]) : 0.0f;
}

static float call_float_3f(UINT64 hash, float f0, float f1, float f2) {
    fn_nativeInit(hash);
    fn_nativePush64(pack_float(f0));
    fn_nativePush64(pack_float(f1));
    fn_nativePush64(pack_float(f2));
    UINT64* r = fn_nativeCall();
    return r ? unpack_float(r[0]) : 0.0f;
}

static uint32_t call_zone_at_coords(float x, float y, float z, int zoneType) {
    fn_nativeInit(0x43AD8FC02B429D33ULL); // ZONE::_GET_MAP_ZONE_AT_COORDS
    fn_nativePush64(pack_float(x));
    fn_nativePush64(pack_float(y));
    fn_nativePush64(pack_float(z));
    fn_nativePush64((UINT64)(int64_t)zoneType);
    UINT64* r = fn_nativeCall();
    return r ? (uint32_t)r[0] : 0;
}

static void call_vec3_0(UINT64 hash, float* out_x, float* out_y, float* out_z) {
    fn_nativeInit(hash);
    UINT64* r = fn_nativeCall();
    if (r) {
        *out_x = unpack_float(r[0]);
        *out_y = unpack_float(r[1]);
        *out_z = unpack_float(r[2]);
    }
}

static void call_vec3_3(UINT64 hash, UINT64 a0, UINT64 a1, UINT64 a2, float* out_x, float* out_y, float* out_z) {
    fn_nativeInit(hash);
    fn_nativePush64(a0);
    fn_nativePush64(a1);
    fn_nativePush64(a2);
    UINT64* r = fn_nativeCall();
    if (r) {
        *out_x = unpack_float(r[0]);
        *out_y = unpack_float(r[1]);
        *out_z = unpack_float(r[2]);
    }
}

struct NamedHash {
    const char* name;
    uint32_t hash;
};

static const NamedHash WEAPONS_TABLE[] = {
    {"Cattleman Revolver", 0x169F59F7U},
    {"Schofield Revolver", 0x7BBD1FF6U},
    {"Double-Action Revolver", 0x0797FBF5U},
    {"Volcanic Pistol", 0x020D13FFU},
    {"Semi-Auto Pistol", 0x657065D6U},
    {"Mauser Pistol", 0x8580C63EU},
    {"M1899 Pistol", 0x5B78B8DDU},
    {"Carbine Repeater", 0xF5175BA1U},
    {"Lancaster Repeater", 0xA84762ECU},
    {"Litchfield Repeater", 0x95B24592U},
    {"Evans Repeater", 0x7194721EU},
    {"Varmint Rifle", 0xDDF7BC1EU},
    {"Springfield Rifle", 0x63F46DE6U},
    {"Bolt-Action Rifle", 0x772C8DD6U},
    {"Rolling Block Rifle", 0xE1D2B317U},
    {"Carcano Rifle", 0x53944780U},
    {"Double-Barreled Shotgun", 0x6DFA071BU},
    {"Sawed-Off Shotgun", 0x1765A8F8U},
    {"Pump-Action Shotgun", 0x31B7B9FEU},
    {"Semi-Auto Shotgun", 0x6D9BB970U},
    {"Repeating Shotgun", 0x63CA782AU},
    {"Bow", 0x88A8505CU},
    {"Lasso", 0x7A8A724AU}
};

static const char* ARROW_TYPES[] = {
    "AMMO_ARROW",
    "AMMO_ARROW_SMALL_GAME",
    "AMMO_ARROW_IMPROVED",
    "AMMO_ARROW_POISON",
    "AMMO_ARROW_FIRE",
    "AMMO_ARROW_DYNAMITE"
};

struct InventoryQuery {
    const char* key;
    const char* item_id;
};

static const InventoryQuery INVENTORY_TABLE[] = {
    {"buck_antler_trinket", "PROVISION_TRINKET_BUCK_ANTLER"},
    {"ram_horn_trinket", "PROVISION_TRINKET_RAM_HORN"},
    {"wolf_heart_trinket", "PROVISION_TRINKET_WOLF_HEART"},
    {"elk_antler_trinket", "PROVISION_TRINKET_ELK_ANTLER"},
    {"beaver_tooth_trinket", "PROVISION_TRINKET_BEAVER_TOOTH"},
    {"fox_claw_trinket", "PROVISION_TRINKET_FOX_CLAW"},
    {"coyote_fang_trinket", "PROVISION_TRINKET_COYOTE_FANG"},
    {"panther_eye_trinket", "PROVISION_TRINKET_PANTHER_EYE"},
    {"pronghorn_trinket", "PROVISION_TRINKET_PRONGHORN_ANTLER"},
    {"tatanka_bison_trinket", "PROVISION_TRINKET_TATANKA_BISON_HORN"},
    {"legendary_buck_antlers", "PROVISION_BUCK_ANTLERS_LEGENDARY"},
    {"gold_bar", "PROVISION_GOLD_BAR"},
    {"gold_nugget", "PROVISION_GOLD_NUGGET"},
    {"health_cure", "CONSUMABLE_MEDICINE"},
    {"health_cure_alt", "CONSUMABLE_HEALTH_CURE"},
    {"potent_health_cure", "CONSUMABLE_POTENT_MEDICINE"},
    {"potent_health_cure_alt", "CONSUMABLE_POTENT_HEALTH_CURE"},
    {"snake_oil", "CONSUMABLE_SNAKE_OIL"},
    {"potent_snake_oil", "CONSUMABLE_POTENT_SNAKE_OIL"},
    {"miracle_tonic", "CONSUMABLE_TONIC"},
    {"potent_miracle_tonic", "CONSUMABLE_POTENT_TONIC"},
    {"horse_reviver", "CONSUMABLE_HORSE_REVIVER"},
    {"oregano", "CONSUMABLE_HERB_OREGANO"},
    {"creeping_thyme", "CONSUMABLE_HERB_CREEPING_THYME"},
    {"wild_mint", "CONSUMABLE_HERB_WILD_MINT"}
};

struct ChallengeCategory {
    const char* key;
    const char* root_id;
};

static const ChallengeCategory CHALLENGE_CATEGORIES[] = {
    {"bandit",         "SP_CHAL_BAND_ROOT"},
    {"explorer",       "SP_CHAL_EXPL_ROOT"},
    {"gambler",        "SP_CHAL_GAMB_ROOT"},
    {"herbalist",      "SP_CHAL_HERB_ROOT"},
    {"horseman",       "SP_CHAL_HORSE_ROOT"},
    {"master_hunter",  "SP_CHAL_HUNT_ROOT"},
    {"sharpshooter",   "SP_CHAL_SHOT_ROOT"},
    {"survivalist",    "SP_CHAL_SURV_ROOT"},
    {"weapons_expert", "SP_CHAL_WEAP_ROOT"}
};

struct ChallengeGoal {
    uint8_t cat_idx;
    uint8_t rank;
    const char* goal_id;
};

static const ChallengeGoal CHALLENGE_GOALS[] = {
    // 0: Bandit
    {0,  1, "ACW_BAND_RANK_01_TOWNSFOLK"},
    {0,  2, "ACW_BAND_RANK_02_COACHROBBERIES"},
    {0,  3, "ACW_BAND_RANK_03_SHOPROBBERIES"},
    {0,  4, "ACW_BAND_RANK_04_COACHESROBBEDINADAY"},
    {0,  5, "ACW_BAND_RANK_05_HIGHESTBOUNTY"},
    {0,  6, "ACW_BAND_RANK_06_HORSESFENCED"},
    {0,  7, "ACW_BAND_RANK_07_STEALCASH"},
    {0,  8, "ACW_BAND_RANK_08_WAGONSFENCED"},
    {0,  9, "ACW_BAND_RANK_09_HOGTIEDTRAINTRACKS"},
    {0, 10, "ACW_BAND_RANK_10_TRAINROBBERIES"},
    // 1: Explorer
    {1,  1, "ACW_EXPL_RANK_01_TREASURE"},
    {1,  2, "ACW_EXPL_RANK_02_TREASURE"},
    {1,  3, "ACW_EXPL_RANK_03_TREASURE"},
    {1,  4, "ACW_EXPL_RANK_04_TREASURE"},
    {1,  5, "ACW_EXPL_RANK_05_TREASURE"},
    {1,  6, "ACW_EXPL_RANK_06_TREASURE"},
    {1,  7, "ACW_EXPL_RANK_07_TREASURE"},
    {1,  8, "ACW_EXPL_RANK_08_TREASURE"},
    {1,  9, "ACW_EXPL_RANK_09_TREASURE"},
    {1, 10, "ACW_EXPL_RANK_10_TREASURE"},
    // 2: Gambler
    {2,  1, "ACW_GAMB_RANK_01_POKER"},
    {2,  2, "ACW_GAMB_RANK_02_BLACKJACK"},
    {2,  3, "ACW_GAMB_RANK_03_FIVEFINGERFILLET"},
    {2,  4, "ACW_GAMB_RANK_04_POKER_FNS"},
    {2,  4, "ACW_GAMB_RANK_04_POKER_SDN"},
    {2,  4, "ACW_GAMB_RANK_04_POKER_VAL"},
    {2,  5, "ACW_GAMB_RANK_05_DOMINOES"},
    {2,  6, "ACW_GAMB_RANK_06_BLACKJACK_RHO"},
    {2,  6, "ACW_GAMB_RANK_06_BLACKJACK_VAN"},
    {2,  7, "ACW_GAMB_RANK_07_FIVEFINGER_STR"},
    {2,  7, "ACW_GAMB_RANK_07_FIVEFINGER_VAL"},
    {2,  7, "ACW_GAMB_RANK_07_FIVEFINGER_VAN"},
    {2,  8, "ACW_GAMB_RANK_08_BLACKJACK"},
    {2,  9, "ACW_GAMB_RANK_09_DOMINOES"},
    {2, 10, "ACW_GAMB_RANK_10_POKERHANDS"},
    // 3: Herbalist
    {3,  1, "ACW_HERB_RANK_01_YARROW"},
    {3,  2, "ACW_HERB_RANK_02_BERRIES"},
    {3,  3, "ACW_HERB_RANK_03_SAGECRAFTING"},
    {3,  4, "ACW_HERB_RANK_04_FEEDMUSHROOMS"},
    {3,  4, "ACW_HERB_RANK_04_POTENTHERBIVOREBAIT"},
    {3,  5, "ACW_HERB_RANK_05_TOBACCOCRAFTING"},
    {3,  6, "ACW_HERB_RANK_06_PICKINGHERBS"},
    {3,  7, "ACW_HERB_RANK_07_CRAFTSPECIALTONIC"},
    {3,  7, "ACW_HERB_RANK_07_USESPECIALTONIC"},
    {3,  8, "ACW_HERB_RANK_08_POISONWEAPONS"},
    {3,  9, "ACW_HERB_RANK_09_ALLHERBS"},
    {3, 10, "ACW_HERB_RANK_10_BIGGAMEMEATSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_CRUSTACEANMEATSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_EXOTICBIRDSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_FLAKEYFISHSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_GAMEMEATSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_GRISTLYMUTTONSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_MATUREVENISONSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_PLUMPBIRDSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_PRIMEBEEFSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_SUCCULENTFISHSEASONING"},
    {3, 10, "ACW_HERB_RANK_10_TENDERPORKSEASONING"},
    // 4: Horseman
    {4,  1, "ACW_HORSE_RANK_01_RABBITS"},
    {4,  2, "ACW_HORSE_RANK_02_OBSTACLES"},
    {4,  3, "ACW_HORSE_RANK_03_TIMEDRIDE"},
    {4,  4, "ACW_HORSE_RANK_04_LASSODRAG"},
    {4,  5, "ACW_HORSE_RANK_05_TRAMPLE"},
    {4,  6, "ACW_HORSE_RANK_06_TIMEDRIDE"},
    {4,  7, "ACW_HORSE_RANK_07_KILLNODISMOUNT"},
    {4,  8, "ACW_HORSE_RANK_08_PREDATORS"},
    {4,  9, "ACW_HORSE_RANK_09_TIMEDRIDE"},
    {4, 10, "ACW_HORSE_RANK_10_AMERICAN_PAINT"},
    {4, 10, "ACW_HORSE_RANK_10_AMERICAN_STANDARDBRED"},
    {4, 10, "ACW_HORSE_RANK_10_APPALOOSA"},
    {4, 10, "ACW_HORSE_RANK_10_ARABIAN"},
    {4, 10, "ACW_HORSE_RANK_10_HUNGARIAN"},
    {4, 10, "ACW_HORSE_RANK_10_KENTUCKY"},
    {4, 10, "ACW_HORSE_RANK_10_MORGAN"},
    {4, 10, "ACW_HORSE_RANK_10_MUSTANG"},
    {4, 10, "ACW_HORSE_RANK_10_NOKOTA"},
    {4, 10, "ACW_HORSE_RANK_10_TENNESSEE"},
    // 5: Master Hunter
    {5,  1, "ACW_HUNT_RANK_01_SKIN"},
    {5,  2, "ACW_HUNT_RANK_02_RABBITS"},
    {5,  3, "ACW_HUNT_RANK_03_BINOCULARS"},
    {5,  4, "ACW_HUNT_RANK_04_CLEANKILL"},
    {5,  5, "ACW_HUNT_RANK_05_BEAR"},
    {5,  6, "ACW_HUNT_RANK_06_COUGARKILL"},
    {5,  6, "ACW_HUNT_RANK_06_COUGARSKIN"},
    {5,  7, "ACW_HUNT_RANK_07_BAITEDKILLS"},
    {5,  8, "ACW_HUNT_RANK_08_LOOTEDFISH"},
    {5,  9, "ACW_HUNT_RANK_09_POSSUM"},
    {5, 10, "ACW_HUNT_RANK_10_PANTHER"},
    // 6: Sharpshooter
    {6,  1, "ACW_SHOT_RANK_01_FLYING"},
    {6,  2, "ACW_SHOT_RANK_02_ANIMALS"},
    {6,  3, "ACW_SHOT_RANK_03_TRAIN"},
    {6,  4, "ACW_SHOT_RANK_04_TOMAHAWK"},
    {6,  5, "ACW_SHOT_RANK_05_SWITCHING"},
    {6,  6, "ACW_SHOT_RANK_06_SCOPEDRIFLE"},
    {6,  7, "ACW_SHOT_RANK_07_HEADSHOTS"},
    {6,  8, "ACW_SHOT_RANK_08_DISARM"},
    {6,  9, "ACW_SHOT_RANK_09_DISARM"},
    {6, 10, "ACW_SHOT_RANK_10_SNIPERRIFLE"},
    // 7: Survivalist
    {7,  1, "ACW_SURV_RANK_01_BLUEGILL"},
    {7,  2, "ACW_SURV_RANK_02_CARCASSDONATION"},
    {7,  3, "ACW_SURV_RANK_03_VARMINTRIFLE"},
    {7,  4, "ACW_SURV_RANK_04_DYNAMITEARROW"},
    {7,  4, "ACW_SURV_RANK_04_FIREARROW"},
    {7,  4, "ACW_SURV_RANK_04_IMPROVEDARROW"},
    {7,  4, "ACW_SURV_RANK_04_POISONARROW"},
    {7,  4, "ACW_SURV_RANK_04_SMALLGAMEARROW"},
    {7,  5, "ACW_SURV_RANK_05_FISHINGRIVERBOAT"},
    {7,  5, "ACW_SURV_RANK_05_FISHINGTRACKS"},
    {7,  6, "ACW_SURV_RANK_06_SCAVENGERKILL"},
    {7,  7, "ACW_SURV_RANK_07_SMALLGAME"},
    {7,  8, "ACW_SURV_RANK_08_HOMINGTOMAHAWK"},
    {7,  8, "ACW_SURV_RANK_08_IMPROVEDTOMAHAWK"},
    {7,  8, "ACW_SURV_RANK_08_VOLATILEDYNAMITE"},
    {7,  8, "ACW_SURV_RANK_08_VOLATILEFIREBOTTLE"},
    {7,  9, "ACW_SURV_RANK_09_HEAVYFISHCAUGHT"},
    {7, 10, "ACW_SURV_RANK_10_BLUEGILL"},
    {7, 10, "ACW_SURV_RANK_10_BULLHEADCATFISH"},
    {7, 10, "ACW_SURV_RANK_10_CHAINPICKEREL"},
    {7, 10, "ACW_SURV_RANK_10_CHANNELCATFISH"},
    {7, 10, "ACW_SURV_RANK_10_LAKESTURGEON"},
    {7, 10, "ACW_SURV_RANK_10_LARGEMOUTHBASS"},
    {7, 10, "ACW_SURV_RANK_10_LONGNOSEGAR"},
    {7, 10, "ACW_SURV_RANK_10_MUSKIE"},
    {7, 10, "ACW_SURV_RANK_10_NORTHERNPIKE"},
    {7, 10, "ACW_SURV_RANK_10_PERCH"},
    {7, 10, "ACW_SURV_RANK_10_REDFINPICKEREL"},
    {7, 10, "ACW_SURV_RANK_10_ROCKBASS"},
    {7, 10, "ACW_SURV_RANK_10_SMALLMOUTHBASS"},
    {7, 10, "ACW_SURV_RANK_10_SOCKEYESALMON"},
    {7, 10, "ACW_SURV_RANK_10_STEELHEADTROUT"},
    // 8: Weapons Expert
    {8,  1, "ACW_WEAP_RANK_01_KNIFEKILLS"},
    {8,  2, "ACW_WEAP_RANK_02_THROWINGKNIFE"},
    {8,  3, "ACW_WEAP_RANK_03_TOMAHAWK"},
    {8,  4, "ACW_WEAP_RANK_04_SHOTGUNCRAFTEDAMMO"},
    {8,  5, "ACW_WEAP_RANK_05_MOUNTED"},
    {8,  6, "ACW_WEAP_RANK_06_DYNAMITE"},
    {8,  7, "ACW_WEAP_RANK_07_TOMAHAWK"},
    {8,  8, "ACW_WEAP_RANK_08_SIDEARM"},
    {8,  9, "ACW_WEAP_RANK_09_BOW"},
    {8, 10, "ACW_WEAP_RANK_10_BEAR"}
};

static int ReadGlobalInt(int globalId) {
    if (!fn_getGlobalPtr) return -1;
    UINT64* ptr = fn_getGlobalPtr(globalId);
    if (!ptr) return -1;
    return (int)(int64_t)(*ptr);
}

static void BuildCampUpgradesJson(char* out_buf, size_t out_size) {
    // Verified from RDR2 1491.50 camp_horseshoeoverlook.ysc (Global_40.f_4283.f_313..f_322)
    // Raw script values are 1-based (1 = base/unpurchased, 2 = Tier 1, 3 = Tier 2, 4 = Tier 3)
    const int BASE = 40 + 4283;
    int raw_chickens = ReadGlobalInt(BASE + 313);
    int raw_boat     = ReadGlobalInt(BASE + 314);
    int raw_leather  = ReadGlobalInt(BASE + 315);
    int raw_prov     = ReadGlobalInt(BASE + 318);
    int raw_med      = ReadGlobalInt(BASE + 319);
    int raw_ammo     = ReadGlobalInt(BASE + 320);
    int raw_lodging  = ReadGlobalInt(BASE + 321);
    int raw_horse    = ReadGlobalInt(BASE + 322);

    auto to_level = [](int raw, int max_lvl) -> int {
        if (raw <= 1) return 0;
        int lvl = raw - 1;
        return lvl > max_lvl ? max_lvl : lvl;
    };

    snprintf(out_buf, out_size,
        "{"
        "\"available\":%s,"
        "\"lodging\":{\"level\":%d,\"max_level\":3,\"raw\":%d},"
        "\"provisions\":{\"level\":%d,\"max_level\":3,\"raw\":%d},"
        "\"medicine\":{\"level\":%d,\"max_level\":3,\"raw\":%d},"
        "\"munitions\":{\"level\":%d,\"max_level\":3,\"raw\":%d},"
        "\"leather_working_tools\":{\"level\":%d,\"max_level\":1,\"raw\":%d},"
        "\"horse_station\":{\"level\":%d,\"max_level\":1,\"raw\":%d},"
        "\"chicken_coop\":{\"level\":%d,\"max_level\":1,\"raw\":%d},"
        "\"boat\":{\"level\":%d,\"max_level\":1,\"raw\":%d}"
        "}",
        (fn_getGlobalPtr != nullptr && raw_lodging >= 0) ? "true" : "false",
        to_level(raw_lodging, 3), raw_lodging,
        to_level(raw_prov, 3), raw_prov,
        to_level(raw_med, 3), raw_med,
        to_level(raw_ammo, 3), raw_ammo,
        to_level(raw_leather, 1), raw_leather,
        to_level(raw_horse, 1), raw_horse,
        to_level(raw_chickens, 1), raw_chickens,
        to_level(raw_boat, 1), raw_boat
    );
}

struct TrinketQuery {
    const char* key;
    const char* item_id;
};

static const TrinketQuery TRINKETS_TABLE[] = {
    // 6 Talismans
    {"alligator_tooth_talisman", "PROVISION_TALISMAN_ALLIGATOR_TOOTH"},
    {"bear_claw_talisman",       "PROVISION_TALISMAN_BEAR_CLAW"},
    {"bison_horn_talisman",      "PROVISION_TALISMAN_BUFFALO_HORN"},
    {"boar_tusk_talisman",       "PROVISION_TALISMAN_BOAR_TUSK"},
    {"raven_claw_talisman",      "PROVISION_TALISMAN_RAVEN_CLAW"},
    {"eagle_talon_talisman",     "PROVISION_TALISMAN_EAGLE_TALON"},
    // 13 Craftable Legendary Animal Trinkets
    {"beaver_tooth_trinket",       "PROVISION_TRINKET_BEAVER_TOOTH"},
    {"buck_antler_trinket",        "PROVISION_TRINKET_BUCK_ANTLER"},
    {"cougar_fang_trinket",        "PROVISION_TRINKET_COUGAR_FANG"},
    {"coyote_fang_trinket",        "PROVISION_TRINKET_COYOTE_FANG"},
    {"elk_antler_trinket",         "PROVISION_TRINKET_ELK_ANTLER"},
    {"fox_claw_trinket",           "PROVISION_TRINKET_FOX_CLAW"},
    {"lion_paw_trinket",           "PROVISION_TRINKET_LION_PAW"},
    {"moose_antler_trinket",       "PROVISION_TRINKET_MOOSE_ANTLER"},
    {"panther_eye_trinket",        "PROVISION_TRINKET_PANTHER_EYE"},
    {"pronghorn_horn_trinket",     "PROVISION_TRINKET_PRONGHORN_ANTLER"},
    {"ram_horn_trinket",           "PROVISION_TRINKET_RAM_HORN"},
    {"tatanka_bison_horn_trinket", "PROVISION_TRINKET_BISON_HORN"},
    {"wolf_heart_trinket",         "PROVISION_TRINKET_WOLF_HEART"},
    // 6 World-Found / Quest Trinkets
    {"cat_eye_trinket",      "PROVISION_TRINKET_CAT_EYE"},
    {"crow_beak_trinket",    "PROVISION_TRINKET_CROW_BEAK"},
    {"hawk_talon_trinket",   "PROVISION_TRINKET_HAWK_TALON"},
    {"owl_feather_trinket",  "PROVISION_TRINKET_OWL_FEATHER"},
    {"shark_tooth_trinket",  "PROVISION_TRINKET_SHARK_TOOTH"},
    {"turtle_shell_trinket", "PROVISION_TRINKET_TURTLE_SHELL"}
};

static const TrinketQuery TALISMAN_INGREDIENTS_TABLE[] = {
    {"silver_chain_bracelet",       "PROVISION_BRACELET_SILVER"},
    {"quartz_chunk",                "PROVISION_RC_QUARTZ_CHUNK"},
    {"gold_jointed_bracelet",       "PROVISION_BRACELET_GOLD"},
    {"vintage_civil_war_handcuffs", "PROVISION_CC_VINTAGE_HANDCUFFS"},
    {"abalone_shell_fragment",      "PROVISION_RS_ABALONE_SHELL_FRAGMENT"},
    {"silver_earring",              "PROVISION_EARRING_SILVER"},
    {"gold_earring",                "PROVISION_EARRING_GOLD"},
    {"cobalt_petrified_wood",       "PROVISION_RF_WOOD_COBALT"},
    {"old_brass_compass",           "PROVISION_TH_ANTIQUE_BRASS_COMPASS"}
};

static void BuildTrinketsJson(int inv_id, char* out_buf, size_t out_size) {
    int pos = snprintf(out_buf, out_size, "{\"owned\":{");
    size_t t_count = sizeof(TRINKETS_TABLE) / sizeof(TRINKETS_TABLE[0]);
    for (size_t i = 0; i < t_count && pos < (int)out_size - 96; ++i) {
        int qty = call_int_3(0xE787F05DFC977BDEULL, (UINT64)inv_id, (UINT64)joaat(TRINKETS_TABLE[i].item_id), 0);
        pos += snprintf(out_buf + pos, out_size - pos, "%s\"%s\":%d", i == 0 ? "" : ",", TRINKETS_TABLE[i].key, qty);
    }
    pos += snprintf(out_buf + pos, out_size - pos, "},\"ingredients\":{");
    size_t ing_count = sizeof(TALISMAN_INGREDIENTS_TABLE) / sizeof(TALISMAN_INGREDIENTS_TABLE[0]);
    for (size_t i = 0; i < ing_count && pos < (int)out_size - 64; ++i) {
        int qty = call_int_3(0xE787F05DFC977BDEULL, (UINT64)inv_id, (UINT64)joaat(TALISMAN_INGREDIENTS_TABLE[i].item_id), 0);
        pos += snprintf(out_buf + pos, out_size - pos, "%s\"%s\":%d", i == 0 ? "" : ",", TALISMAN_INGREDIENTS_TABLE[i].key, qty);
    }
    snprintf(out_buf + pos, out_size - pos, "}}");
}

static void BuildChallengesJson(char* out_buf, size_t out_size) {
    int pos = snprintf(out_buf, out_size, "{");
    size_t cat_count = sizeof(CHALLENGE_CATEGORIES) / sizeof(CHALLENGE_CATEGORIES[0]);
    size_t goal_count = sizeof(CHALLENGE_GOALS) / sizeof(CHALLENGE_GOALS[0]);

    for (size_t c = 0; c < cat_count && pos < (int)out_size - 256; ++c) {
        uint32_t chal_hash = joaat(CHALLENGE_CATEGORIES[c].root_id);
        int completed = call_int_1(0x58CB53DB63F84DE9ULL, (UINT64)chal_hash); // STATS::CHAL_GET_NUM_RANKS_COMPLETED
        int max_ranks = call_int_1(0x58CB53DB63F84DEAULL, (UINT64)chal_hash); // STATS::CHAL_GET_MAX_RANKS
        if (max_ranks <= 0) max_ranks = 10;
        if (completed < 0) completed = 0;
        if (completed > max_ranks) completed = max_ranks;
        int active_rank = (completed < max_ranks) ? (completed + 1) : 0;

        pos += snprintf(out_buf + pos, out_size - pos,
                        "%s\"%s\":{\"ranks_completed\":%d,\"max_ranks\":%d,\"active_rank\":%d,\"goals\":[",
                        c == 0 ? "" : ",",
                        CHALLENGE_CATEGORIES[c].key,
                        completed, max_ranks, active_rank);

        if (active_rank > 0) {
            int first_g = 1;
            for (size_t g = 0; g < goal_count && pos < (int)out_size - 160; ++g) {
                if (CHALLENGE_GOALS[g].cat_idx == c && CHALLENGE_GOALS[g].rank == active_rank) {
                    uint32_t goal_hash = joaat(CHALLENGE_GOALS[g].goal_id);
                    int prog = call_int_2(0x808712E428F697B8ULL, (UINT64)chal_hash, (UINT64)goal_hash); // CHAL_ACHIEVEMENT_GET_PROGRESS_INT
                    int is_comp = call_int_2(0x77B97A827739D434ULL, (UINT64)chal_hash, (UINT64)goal_hash); // CHAL_ACHIEVEMENT_IS_COMPLETE
                    int is_act = call_int_2(0x04DAC3929796EB87ULL, (UINT64)chal_hash, (UINT64)goal_hash); // CHAL_IS_GOAL_ACTIVE
                    pos += snprintf(out_buf + pos, out_size - pos,
                                    "%s{\"id\":\"%s\",\"progress\":%d,\"complete\":%s,\"active\":%s}",
                                    first_g ? "" : ",",
                                    CHALLENGE_GOALS[g].goal_id,
                                    prog,
                                    is_comp ? "true" : "false",
                                    is_act ? "true" : "false");
                    first_g = 0;
                }
            }
        }
        pos += snprintf(out_buf + pos, out_size - pos, "]}");
    }
    snprintf(out_buf + pos, out_size - pos, "}");
}

static const char* LookupWeaponName(uint32_t hash) {
    if (hash == 0 || hash == 0xA2719263U) return "Unarmed";
    size_t count = sizeof(WEAPONS_TABLE) / sizeof(WEAPONS_TABLE[0]);
    for (size_t i = 0; i < count; ++i) {
        if (WEAPONS_TABLE[i].hash == hash) return WEAPONS_TABLE[i].name;
    }
    return nullptr;
}

static bool ExtractJsonFloat(const char* body, const char* key, float* out_val) {
    char pattern[32];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char* p = strstr(body, pattern);
    if (!p) return false;
    p += strlen(pattern);
    while (*p && (*p == ' ' || *p == ':' || *p == '\t')) p++;
    if (!*p) return false;
    char* endp = nullptr;
    float v = strtof(p, &endp);
    if (endp == p) return false;
    *out_val = v;
    return true;
}

static DWORD WINAPI HttpServerThread(LPVOID) {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return 1;

    SOCKET listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listen_sock == INVALID_SOCKET) {
        WSACleanup();
        return 1;
    }
    g_listen_sock = listen_sock;

    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));

    sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(SERVER_PORT);

    if (bind(listen_sock, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(listen_sock);
        g_listen_sock = INVALID_SOCKET;
        WSACleanup();
        return 1;
    }

    listen(listen_sock, 8);

    while (g_running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(listen_sock, &read_fds);

        timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 500000;
        int sel = select(0, &read_fds, nullptr, nullptr, &tv);
        if (!g_running) break;
        if (sel > 0 && FD_ISSET(listen_sock, &read_fds)) {
            SOCKET client_sock = accept(listen_sock, nullptr, nullptr);
            if (client_sock != INVALID_SOCKET) {
                char req_buf[4096];
                memset(req_buf, 0, sizeof(req_buf));
                int bytes = recv(client_sock, req_buf, sizeof(req_buf) - 1, 0);
                if (bytes > 0) {
                    char resp_body[16384];
                    if (strncmp(req_buf, "POST /waypoint", 14) == 0) {
                        const char* hdr_end = strstr(req_buf, "\r\n\r\n");
                        if (hdr_end && *(hdr_end + 4) == '\0' && bytes < (int)sizeof(req_buf) - 1) {
                            int extra = recv(client_sock, req_buf + bytes, (int)sizeof(req_buf) - 1 - bytes, 0);
                            if (extra > 0) bytes += extra;
                        }
                        const char* body = hdr_end ? (hdr_end + 4) : req_buf;
                        float x = 0.0f, y = 0.0f, z = 0.0f;
                        if (ExtractJsonFloat(body, "x", &x) && ExtractJsonFloat(body, "y", &y)) {
                            ExtractJsonFloat(body, "z", &z);
                            g_wp_x = x;
                            g_wp_y = y;
                            g_wp_z = z;
                            InterlockedExchange(&g_pending_wp, 1);
                            snprintf(resp_body, sizeof(resp_body),
                                     "{\"success\":true,\"queued\":{\"x\":%.2f,\"y\":%.2f,\"z\":%.2f}}", x, y, z);
                        } else {
                            snprintf(resp_body, sizeof(resp_body),
                                     "{\"success\":false,\"error\":\"Invalid waypoint JSON body\"}");
                        }
                    } else {
                        EnterCriticalSection(&g_cs);
                        snprintf(resp_body, sizeof(resp_body), "%s", g_json_buf);
                        LeaveCriticalSection(&g_cs);
                    }

                    char header[512];
                    int body_len = (int)strlen(resp_body);
                    int hdr_len = snprintf(header, sizeof(header),
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        "Access-Control-Allow-Origin: *\r\n"
                        "Content-Length: %d\r\n"
                        "Connection: close\r\n\r\n",
                        body_len);
                    send(client_sock, header, hdr_len, 0);
                    send(client_sock, resp_body, body_len, 0);
                }
                closesocket(client_sock);
            }
        }
    }

    if (g_listen_sock != INVALID_SOCKET) {
        closesocket(g_listen_sock);
        g_listen_sock = INVALID_SOCKET;
    }
    WSACleanup();
    return 0;
}

static void ClearGpsMultiRoute() {
    // MAP::SET_GPS_MULTI_ROUTE_RENDER(0)
    fn_nativeInit(0x4426D65E029A4DC0ULL);
    fn_nativePush64(0);
    fn_nativeCall();

    // MAP::CLEAR_GPS_MULTI_ROUTE()
    fn_nativeInit(0x9E0AB9AAEE87CE28ULL);
    fn_nativeCall();

    g_gps_route_active = false;
    g_gps_refresh_ticks = 0;
}

static void ApplyGpsMultiRoute() {
    fn_nativeInit(0x9E0AB9AAEE87CE28ULL); // MAP::CLEAR_GPS_MULTI_ROUTE
    fn_nativeCall();

    fn_nativeInit(0x3D3D15AF7BCAAF83ULL); // MAP::START_GPS_MULTI_ROUTE
    fn_nativePush64((UINT64)joaat("COLOR_WAYPOINT"));
    fn_nativePush64(1);
    fn_nativePush64(1);
    fn_nativeCall();

    fn_nativeInit(0x64C59DD6834FA942ULL); // MAP::ADD_POINT_TO_GPS_MULTI_ROUTE
    fn_nativePush64(pack_float(g_wp_x));
    fn_nativePush64(pack_float(g_wp_y));
    fn_nativePush64(pack_float(g_wp_z));
    fn_nativePush64(0);
    fn_nativeCall();

    fn_nativeInit(0x4426D65E029A4DC0ULL); // MAP::SET_GPS_MULTI_ROUTE_RENDER
    fn_nativePush64(1);
    fn_nativeCall();
}

static bool ProcessPendingWaypoint() {
    if (InterlockedCompareExchange(&g_pending_wp, 0, 1) == 1) {
        ClearGpsMultiRoute();

        // MAP::SET_WAYPOINT_OFF()
        fn_nativeInit(0xFA8C41E8020D3439ULL);
        fn_nativeCall();

        if (fabsf(g_wp_x) < 0.01f && fabsf(g_wp_y) < 0.01f) {
            return false;
        }

        ApplyGpsMultiRoute();

        g_gps_route_active = true;
        g_gps_refresh_ticks = 0;
        return true;
    }
    return false;
}

static void TickTelemetryOnce() {
    if (InterlockedCompareExchange(&g_inTick, 1, 0) != 0) return;

    bool just_set_wp = ProcessPendingWaypoint();

    int playerId = call_int_0(0x217E9DC48139933DULL);      // PLAYER::PLAYER_ID
    int playerPed = call_int_0(0x096275889B8E0EE0ULL);     // PLAYER::PLAYER_PED_ID

    static char local_buf[16384];
    if (!playerPed || !call_int_1(0xD42BD6EB2E0F1677ULL, (UINT64)playerPed)) {
        snprintf(local_buf, sizeof(local_buf),
                 "{\"bridge_active\":true,\"in_game\":false,\"message\":\"Player ped not active yet (loading/menu)\"}");
    } else {
            float px = 0.0f, py = 0.0f, pz = 0.0f;
            call_vec3_3(0xA86D5F069399F44DULL, (UINT64)playerPed, 1, 1, &px, &py, &pz); // GET_ENTITY_COORDS
            float heading = call_float_1(0xC230DD956E2F5507ULL, (UINT64)playerPed);      // GET_ENTITY_HEADING
            int health = call_int_1(0x82368787EA73C0F7ULL, (UINT64)playerPed);           // GET_ENTITY_HEALTH
            int max_health = call_int_2(0x15D757606D170C3CULL, (UINT64)playerPed, 0);    // GET_ENTITY_MAX_HEALTH

            int health_core = call_int_2(0x36731AC041289BB1ULL, (UINT64)playerPed, 0);   // _GET_ATTRIBUTE_CORE_VALUE
            int stamina_core = call_int_2(0x36731AC041289BB1ULL, (UINT64)playerPed, 1);
            int dead_eye_core = call_int_2(0x36731AC041289BB1ULL, (UINT64)playerPed, 2);

            int health_rank = call_int_2(0xA4C8E23E29040DE0ULL, (UINT64)playerPed, 0);   // GET_ATTRIBUTE_RANK
            int stamina_rank = call_int_2(0xA4C8E23E29040DE0ULL, (UINT64)playerPed, 1);
            int dead_eye_rank = call_int_2(0xA4C8E23E29040DE0ULL, (UINT64)playerPed, 2);

            int cash_cents = call_int_0(0x0C02DABFA3B98176ULL);                          // _MONEY_GET_CASH_BALANCE
            int bounty_cents = call_int_1(0x54310AAB97B92816ULL, (UINT64)playerId);      // LAW::GET_BOUNTY
            int wanted_level = call_int_1(0xABC532F9098BFD9DULL, (UINT64)playerId);      // GET_PLAYER_WANTED_LEVEL

            int hours = call_int_0(0xC82CF208C2B19199ULL);                               // GET_CLOCK_HOURS
            int minutes = call_int_0(0x4E162231B823DBBFULL);                             // GET_CLOCK_MINUTES
            float temp_c = call_float_3f(0xB98B78C3768AF6E0ULL, px, py, pz);             // _GET_TEMPERATURE_AT_COORDS

            uint32_t state_hash = call_zone_at_coords(px, py, pz, 0);
            uint32_t town_hash = call_zone_at_coords(px, py, pz, 1);
            uint32_t district_hash = call_zone_at_coords(px, py, pz, 10);

            int wp_active = call_int_0(0x202B1BBFC6AB5EE4ULL);                           // IS_WAYPOINT_ACTIVE
            float wpx = 0.0f, wpy = 0.0f, wpz = 0.0f;
            if (wp_active) {
                call_vec3_0(0x29B30D07C3F7873BULL, &wpx, &wpy, &wpz);                    // _GET_WAYPOINT_COORDS
            }
            if (g_gps_route_active && !just_set_wp) {
                float dx_wp = px - g_wp_x, dy_wp = py - g_wp_y;
                if (wp_active != 0 || sqrtf(dx_wp * dx_wp + dy_wp * dy_wp) < 45.0f) {
                    ClearGpsMultiRoute();
                } else if (++g_gps_refresh_ticks >= 15) {
                    g_gps_refresh_ticks = 0;
                    ApplyGpsMultiRoute();
                }
            }

            // Horse telemetry
            int on_mount = call_int_1(0x460BC76A0E10655EULL, (UINT64)playerPed);         // IS_PED_ON_MOUNT
            int mount = call_int_1(0xE7E11B8DCBED1058ULL, (UINT64)playerPed);            // GET_MOUNT
            if (!mount || !call_int_1(0xD42BD6EB2E0F1677ULL, (UINT64)mount)) {
                mount = call_int_1(0x4C8B59171957BCF7ULL, (UINT64)playerPed);            // _GET_LAST_MOUNT
            }
            if (!mount || !call_int_1(0xD42BD6EB2E0F1677ULL, (UINT64)mount)) {
                mount = call_int_1(0xF49F14462F0AE27CULL, (UINT64)playerId);             // GET_MOUNT_OWNED_BY_PLAYER
            }

            int has_horse = (mount && call_int_1(0xD42BD6EB2E0F1677ULL, (UINT64)mount)) ? 1 : 0;
            float hx = 0.0f, hy = 0.0f, hz = 0.0f, h_dist = 0.0f;
            int h_health = 0, h_max_health = 0, h_health_core = 0, h_stamina_core = 0, h_bonding = 0;
            uint32_t h_model = 0;
            if (has_horse) {
                call_vec3_3(0xA86D5F069399F44DULL, (UINT64)mount, 1, 1, &hx, &hy, &hz);
                float dx = px - hx, dy = py - hy, dz = pz - hz;
                h_dist = sqrtf(dx * dx + dy * dy + dz * dz);
                h_health = call_int_1(0x82368787EA73C0F7ULL, (UINT64)mount);
                h_max_health = call_int_2(0x15D757606D170C3CULL, (UINT64)mount, 0);
                h_health_core = call_int_2(0x36731AC041289BB1ULL, (UINT64)mount, 0);
                h_stamina_core = call_int_2(0x36731AC041289BB1ULL, (UINT64)mount, 1);
                h_bonding = call_int_2(0xA4C8E23E29040DE0ULL, (UINT64)mount, 7);         // PA_BONDING = 7
                h_model = call_u32_1(0xDA76A9F39210D365ULL, (UINT64)mount);              // GET_ENTITY_MODEL
            }

            // Active weapon
            uint32_t cur_weapon_hash = 0;
            call_int_5(0x3A87E44BB9A01D54ULL, (UINT64)playerPed, (UINT64)&cur_weapon_hash, 1, 0, 0);
            const char* cur_wep_name = LookupWeaponName(cur_weapon_hash);
            char cur_wep_buf[64];
            if (cur_wep_name) {
                snprintf(cur_wep_buf, sizeof(cur_wep_buf), "%s", cur_wep_name);
            } else {
                snprintf(cur_wep_buf, sizeof(cur_wep_buf), "0x%08X", cur_weapon_hash);
            }

            // Build weapons JSON array
            char weapons_json[2048];
            int wpos = snprintf(weapons_json, sizeof(weapons_json), "[");
            size_t wep_count = sizeof(WEAPONS_TABLE) / sizeof(WEAPONS_TABLE[0]);
            int first_w = 1;
            for (size_t i = 0; i < wep_count && wpos < (int)sizeof(weapons_json) - 128; ++i) {
                int has_w = call_int_4(0x8DECB02F88F428BCULL, (UINT64)playerPed, (UINT64)WEAPONS_TABLE[i].hash, 0, 0);
                if (has_w) {
                    int ammo = call_int_2(0x015A522136D7F951ULL, (UINT64)playerPed, (UINT64)WEAPONS_TABLE[i].hash);
                    wpos += snprintf(weapons_json + wpos, sizeof(weapons_json) - wpos,
                                     "%s{\"name\":\"%s\",\"hash\":\"0x%08X\",\"ammo\":%d}",
                                     first_w ? "" : ",", WEAPONS_TABLE[i].name, WEAPONS_TABLE[i].hash, ammo);
                    first_w = 0;
                }
            }
            snprintf(weapons_json + wpos, sizeof(weapons_json) - wpos, "]");

            // Arrow ammo breakdown
            char arrows_json[512];
            int apos = snprintf(arrows_json, sizeof(arrows_json), "{");
            size_t arr_count = sizeof(ARROW_TYPES) / sizeof(ARROW_TYPES[0]);
            for (size_t i = 0; i < arr_count && apos < (int)sizeof(arrows_json) - 64; ++i) {
                int cnt = call_int_2(0x39D22031557946C1ULL, (UINT64)playerPed, (UINT64)joaat(ARROW_TYPES[i]));
                apos += snprintf(arrows_json + apos, sizeof(arrows_json) - apos,
                                 "%s\"%s\":%d", i == 0 ? "" : ",", ARROW_TYPES[i], cnt);
            }
            snprintf(arrows_json + apos, sizeof(arrows_json) - apos, "}");

            // Inventory / Satchel items & Trinkets
            int inv_id = call_int_1(0x13D234A2A3F66E63ULL, (UINT64)playerPed);
            if (inv_id <= 0) inv_id = 1; // INVENTORY_SP_PLAYER fallback

            char inv_json[2048];
            int ipos = snprintf(inv_json, sizeof(inv_json), "{");
            size_t inv_count = sizeof(INVENTORY_TABLE) / sizeof(INVENTORY_TABLE[0]);
            for (size_t i = 0; i < inv_count && ipos < (int)sizeof(inv_json) - 64; ++i) {
                int qty = call_int_3(0xE787F05DFC977BDEULL, (UINT64)inv_id, (UINT64)joaat(INVENTORY_TABLE[i].item_id), 0);
                ipos += snprintf(inv_json + ipos, sizeof(inv_json) - ipos,
                                 "%s\"%s\":%d", i == 0 ? "" : ",", INVENTORY_TABLE[i].key, qty);
            }
            snprintf(inv_json + ipos, sizeof(inv_json) - ipos, "}");

            // Challenges, Camp Upgrades & Trinkets (refreshed every ~1s = 5 ticks)
            static char challenges_json[4096] = "{}";
            static char camp_upgrades_json[1024] = "{\"available\":false}";
            static char trinkets_json[2048] = "{\"owned\":{},\"ingredients\":{}}";
            if (g_chal_refresh_ticks == 0 || ++g_chal_refresh_ticks >= 5) {
                BuildChallengesJson(challenges_json, sizeof(challenges_json));
                BuildCampUpgradesJson(camp_upgrades_json, sizeof(camp_upgrades_json));
                BuildTrinketsJson(inv_id, trinkets_json, sizeof(trinkets_json));
                g_chal_refresh_ticks = 1;
            }

            snprintf(local_buf, sizeof(local_buf),
                "{\n"
                "  \"bridge_active\": true,\n"
                "  \"in_game\": true,\n"
                "  \"player\": {\n"
                "    \"coords\": {\"x\": %.2f, \"y\": %.2f, \"z\": %.2f},\n"
                "    \"heading\": %.1f,\n"
                "    \"health\": %d,\n"
                "    \"max_health\": %d,\n"
                "    \"health_core\": %d,\n"
                "    \"stamina_core\": %d,\n"
                "    \"dead_eye_core\": %d,\n"
                "    \"health_rank\": %d,\n"
                "    \"stamina_rank\": %d,\n"
                "    \"dead_eye_rank\": %d,\n"
                "    \"cash_cents\": %d,\n"
                "    \"cash_dollars\": %.2f,\n"
                "    \"bounty_raw\": %d,\n"
                "    \"wanted_level\": %d,\n"
                "    \"active_weapon\": \"%s\",\n"
                "    \"active_weapon_hash\": \"0x%08X\",\n"
                "    \"inventory_id\": %d,\n"
                "    \"owned_weapons\": %s,\n"
                "    \"arrows\": %s,\n"
                "    \"inventory\": %s\n"
                "  },\n"
                "  \"horse\": {\n"
                "    \"active\": %s,\n"
                "    \"on_mount\": %s,\n"
                "    \"model_hash\": \"0x%08X\",\n"
                "    \"coords\": {\"x\": %.2f, \"y\": %.2f, \"z\": %.2f},\n"
                "    \"distance\": %.2f,\n"
                "    \"health\": %d,\n"
                "    \"max_health\": %d,\n"
                "    \"health_core\": %d,\n"
                "    \"stamina_core\": %d,\n"
                "    \"bonding_rank\": %d\n"
                "  },\n"
                "  \"world\": {\n"
                "    \"time\": \"%02d:%02d\",\n"
                "    \"temperature_c\": %.1f,\n"
                "    \"state_hash\": \"0x%08X\",\n"
                "    \"town_hash\": \"0x%08X\",\n"
                "    \"district_hash\": \"0x%08X\",\n"
                "    \"waypoint_active\": %s,\n"
                "    \"waypoint_coords\": {\"x\": %.2f, \"y\": %.2f}\n"
                "  },\n"
                "  \"challenges\": %s,\n"
                "  \"camp_upgrades\": %s,\n"
                "  \"trinkets\": %s\n"
                "}",
                px, py, pz,
                heading,
                health, max_health,
                health_core, stamina_core, dead_eye_core,
                health_rank, stamina_rank, dead_eye_rank,
                cash_cents, (double)cash_cents / 100.0,
                bounty_cents, wanted_level,
                cur_wep_buf, cur_weapon_hash,
                inv_id,
                weapons_json,
                arrows_json,
                inv_json,
                has_horse ? "true" : "false",
                on_mount ? "true" : "false",
                h_model,
                hx, hy, hz,
                h_dist,
                h_health, h_max_health,
                h_health_core, h_stamina_core,
                h_bonding,
                hours, minutes,
                temp_c,
                state_hash, town_hash, district_hash,
                wp_active ? "true" : "false",
                wpx, wpy,
                challenges_json,
                camp_upgrades_json,
                trinkets_json
            );
    }

    EnterCriticalSection(&g_cs);
    snprintf(g_json_buf, sizeof(g_json_buf), "%s", local_buf);
    LeaveCriticalSection(&g_cs);

    InterlockedExchange(&g_inTick, 0);
}

static void HookedScriptWait(DWORD dwMilliseconds) {
    if (!InterlockedCompareExchange(&g_scriptMainActive, 0, 0) && g_running) {
        ULONGLONG now = GetTickCount64();
        if (now - g_lastTickMs >= 200) {
            g_lastTickMs = now;
            TickTelemetryOnce();
        }
    }
    if (fn_realScriptWait) {
        fn_realScriptWait(dwMilliseconds);
    }
}

static void ScriptMain() {
    InterlockedExchange(&g_scriptMainActive, 1);
    while (g_running) {
        TickTelemetryOnce();
        if (fn_realScriptWait) fn_realScriptWait(200);
        else if (fn_scriptWait) fn_scriptWait(200);
    }
}

static bool ResolveScriptHook() {
    HMODULE hSH = GetModuleHandleA("ScriptHookRDR2.dll");
    if (!hSH) return false;

    fn_scriptRegister   = (fn_scriptRegister_t)  GetProcAddress(hSH, "?scriptRegister@@YAXPEAUHINSTANCE__@@P6AXXZ@Z");
    fn_scriptUnregister = (fn_scriptUnregister_t)GetProcAddress(hSH, "?scriptUnregister@@YAXPEAUHINSTANCE__@@@Z");
    fn_scriptWait       = (fn_scriptWait_t)      GetProcAddress(hSH, "?scriptWait@@YAXK@Z");
    fn_nativeInit       = (fn_nativeInit_t)      GetProcAddress(hSH, "?nativeInit@@YAX_K@Z");
    fn_nativePush64     = (fn_nativePush64_t)    GetProcAddress(hSH, "?nativePush64@@YAX_K@Z");
    fn_nativeCall       = (fn_nativeCall_t)      GetProcAddress(hSH, "?nativeCall@@YAPEA_KXZ");
    fn_getGlobalPtr     = (fn_getGlobalPtr_t)    GetProcAddress(hSH, "?getGlobalPtr@@YAPEA_KH@Z");

    return (fn_scriptRegister && fn_scriptUnregister && fn_scriptWait &&
            fn_nativeInit && fn_nativePush64 && fn_nativeCall);
}

static void HookScriptWait() {
    if (!fn_scriptWait || g_scriptWaitHooked) return;
    uint8_t* stub = (uint8_t*)fn_scriptWait;
    if (stub[0] != 0xE9) return;

    int32_t rel = 0;
    memcpy(&rel, stub + 1, sizeof(rel));
    fn_realScriptWait = (fn_scriptWait_t)(stub + 5 + rel);
    memcpy(g_origScriptWaitBytes, stub, 16);

    DWORD oldProt = 0;
    if (VirtualProtect(stub, 16, PAGE_EXECUTE_READWRITE, &oldProt)) {
        uint64_t hookAddr = (uint64_t)(uintptr_t)&HookedScriptWait;
        uint8_t patch[16];
        memset(patch, 0xCC, sizeof(patch));
        patch[0] = 0xFF;
        patch[1] = 0x25;
        patch[2] = 0x00;
        patch[3] = 0x00;
        patch[4] = 0x00;
        patch[5] = 0x00;
        memcpy(patch + 6, &hookAddr, sizeof(hookAddr));

        // Write high bytes first while rel32 jump at [0..4] is intact, then atomically swap [0..7]
        memcpy(stub + 8, patch + 8, 8);
        if (((uintptr_t)stub & 7) == 0) {
            LONGLONG first8 = 0;
            memcpy(&first8, patch, 8);
            InterlockedExchange64((volatile LONGLONG*)stub, first8);
        } else {
            memcpy(stub, patch, 8);
        }

        VirtualProtect(stub, 16, oldProt, &oldProt);
        FlushInstructionCache(GetCurrentProcess(), stub, 16);
        g_scriptWaitHooked = true;
    }
}

static void UnhookScriptWait() {
    if (!g_scriptWaitHooked || !fn_scriptWait) return;
    uint8_t* stub = (uint8_t*)fn_scriptWait;
    DWORD oldProt = 0;
    if (VirtualProtect(stub, 16, PAGE_EXECUTE_READWRITE, &oldProt)) {
        if (((uintptr_t)stub & 7) == 0) {
            LONGLONG origFirst8 = 0;
            memcpy(&origFirst8, g_origScriptWaitBytes, 8);
            InterlockedExchange64((volatile LONGLONG*)stub, origFirst8);
        } else {
            memcpy(stub, g_origScriptWaitBytes, 8);
        }
        memcpy(stub + 8, g_origScriptWaitBytes + 8, 8);
        VirtualProtect(stub, 16, oldProt, &oldProt);
        FlushInstructionCache(GetCurrentProcess(), stub, 16);
        g_scriptWaitHooked = false;
    }
}

static void InitBridge(HMODULE hMod) {
    if (ResolveScriptHook()) {
        fn_scriptRegister(hMod, ScriptMain);
        HookScriptWait();
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        g_hModule = hModule;
        if (!g_cs_initialized) {
            InitializeCriticalSection(&g_cs);
            g_cs_initialized = 1;
        }
        InitBridge(hModule);
        if (InterlockedCompareExchange(&g_server_started, 1, 0) == 0) {
            HANDLE hThread = CreateThread(nullptr, 0, HttpServerThread, nullptr, 0, nullptr);
            if (hThread) CloseHandle(hThread);
        }
        break;
    case DLL_PROCESS_DETACH:
        g_running = 0;
        UnhookScriptWait();
        if (g_listen_sock != INVALID_SOCKET) {
            closesocket(g_listen_sock);
            g_listen_sock = INVALID_SOCKET;
        }
        if (fn_scriptUnregister && g_hModule) {
            fn_scriptUnregister(g_hModule);
        }
        break;
    }
    return TRUE;
}
