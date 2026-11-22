# RDR2-MCP: Model Context Protocol Server for Red Dead Redemption 2

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Game](https://img.shields.io/badge/RDR2-v1.0.1491%2B-red.svg)](https://www.rockstargames.com/reddeadredemption2)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> [!CAUTION]
> **Story Mode Only — Do NOT use in Red Dead Online.**  
> This project injects a ScriptHookRDR2 `.asi` plugin and attaches Win32 process inspection APIs to `RDR2.exe`. Using mods or process hooks in Red Dead Online will likely result in a ban.
>
> **No Third-Party Binaries Included:** Requires [ScriptHookRDR2](http://www.dev-c.com/rdr2/scripthookrdr2/) downloaded separately from its official source. No Rockstar Games assets, proprietary binaries, or third-party DLLs are distributed in this repository.

**RDR2-MCP** is an open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) bridge that connects AI assistants and coding agents (such as **Google Antigravity**, **Claude Desktop**, **Claude Code**, **Cursor**, and **VS Code**) directly to a live running session of **Red Dead Redemption 2** (PC Story Mode).

---

## 🌟 Features

* **⚡ Real-Time Player Telemetry (`rdr2_player_state`):** Live query of Arthur's world coordinates (`x, y, z`), heading, region/town & nearest landmark, health/stamina/dead-eye cores & ranks, cash balance, bounty & wanted level, active & owned weapons (including ammo & arrow counts), and consumables/herbs inventory.
* **🏆 Live Challenge Tracking (`rdr2_challenges`):** Tracks all **9 Story Mode challenge categories (90 ranks total)** — Bandit, Explorer, Gambler, Herbalist, Horseman, Master Hunter, Sharpshooter, Survivalist, and Weapons Expert — with completed ranks, active rank objective, live integer progress counters, and multi-subgoal breakdowns.
* **🏕️ Live Camp Upgrades Tracking (`rdr2_camp_upgrades`):** Tracks all **8 Camp Ledger upgrades** (Lodging / Fast Travel Map, Provisions, Medicine, Munitions, Leather Working Tools, Horse Station, Chicken Coop, Camp Boat) with current tier, unlock flags, next tier price, and remaining total cost.
* **📿 Live Trinkets & Talismans Tracker (`rdr2_trinkets`):** Tracks all **25 Story Mode Trinkets & Talismans**, active passive bonuses, missing items with sources, and **9 rare Talisman crafting ingredients** (Silver Chain Bracelet, Quartz Chunk, Abalone Shell Fragment, Cobalt Petrified Wood, etc.) currently in Arthur's satchel.
* **🐴 Horse Tracking (`rdr2_horse_state`):** Monitor your active horse's spawn & mounted status, model hash, distance to Arthur, health/stamina cores & values, and bonding rank.
* **🗺️ World & Environment (`rdr2_world_info`):** Read in-game clock time, ambient temperature (`°C`), active state/town/district names, and waypoint status.
* **🧭 In-Game GPS Waypoints (`rdr2_set_waypoint`):** Programmatically place an in-game red GPS Multi-Route directly onto the minimap and world map using exact `(x, y)` coordinates or built-in named landmarks (towns, Fences, Trappers, and hunting/treasure locations).
* **🎮 In-Game Input & Live Screen Capture (`rdr2_send_input`, `rdr2_capture_screen`):** Send Win32 input actions (`whistle`, `calm`, `brush`, `dead_eye`, `map`, `journal`, `satchel`, etc.) and capture live PNG screenshots of the game window for visual analysis.
* **📖 Offline RDR2 Encyclopedia (`rdr2_encyclopedia`):** Instant lookup database for legendary animal locations & trinkets/talismans, hunting weapon tiers, Pearson satchel recipes, and camp upgrades.
* **🔌 Hybrid Dual Bridge Architecture:**
  1. **Native In-Game Bridge (`RDR2_MCP_Bridge.asi`):** ScriptHookRDR2 plugin exposing live native telemetry and GPS waypoint routing via both an automatic PE-export direct-memory fast-path (`ReadProcessMemory`/`WriteProcessMemory`) and an embedded local HTTP server (`http://127.0.0.1:28999`).
  2. **Non-Invasive Process Bridge (Fallback):** Automatically falls back to Windows Toolhelp process/window inspection and GDI/Win32 screen capture when the `.asi` bridge is not present.

---

## 🏛️ Architecture

```
+-----------------------------------------------------------------------------------+
|                           Red Dead Redemption 2 (PC)                              |
|                                                                                   |
|  [ RDR2_MCP_Bridge.asi (ScriptHookRDR2) ]          [ RDR2.exe Process & Window ]  |
|   Exported Shared State + HTTP (:28999)                  GDI/Win32 Capture        |
+-----------------------------------------------------------------------------------+
                             ▲                                    ▲
                             │ Win32 Memory (PE Exports) / HTTP   │ Win32 API
                             ▼                                    ▼
+-----------------------------------------------------------------------------------+
|                             rdr2-mcp Python Server                                |
|                                                                                   |
|  - Dynamic PE Export RVA Bridge (Direct Memory / HTTP + Win32 Fallback)           |
|  - Live Trackers (Challenges, Camp Upgrades, Trinkets & Talismans)                |
|  - Offline RDR2 Encyclopedia (Hunting, Satchels, Trinkets, Camp Upgrades)         |
|  - Standard Model Context Protocol (MCP 2024-11-05 Stdio Transport)               |
+-----------------------------------------------------------------------------------+
                                         ▲
                                         │ JSON-RPC (stdio)
                                         ▼
+-----------------------------------------------------------------------------------+
|                             AI Assistant / Agent                                  |
|         (Google Antigravity, Claude Desktop, Claude Code, Cursor, VS Code)        |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Available MCP Tools

| Tool | Description |
|---|---|
| `rdr2_status` | Checks the connection status to `RDR2.exe`, active process info, window resolution, and bridge mode. |
| `rdr2_player_state` | Retrieves Arthur's live coordinates, heading, region, nearest landmark, cores/ranks, cash, bounty/wanted status, weapons, ammo, and inventory. |
| `rdr2_horse_state` | Retrieves the active horse's mounted state, distance, health, stamina, model hash, and bonding rank. |
| `rdr2_world_info` | Retrieves the in-game clock time, temperature (`°C`), state/town/district, and waypoint state. |
| `rdr2_challenges` | Retrieves live Story Mode challenge progress across all 9 categories (`bandit`, `explorer`, `gambler`, `herbalist`, `horseman`, `master_hunter`, `sharpshooter`, `survivalist`, `weapons_expert`). |
| `rdr2_camp_upgrades` | Retrieves live Camp Ledger upgrade status (Lodging / Fast Travel Map, Provisions, Medicine, Munitions, Leather Working Tools, Horse Station, Chicken Coop, Boat) and remaining cost. |
| `rdr2_trinkets` | Retrieves live status of all 25 Trinkets & Talismans (`all`, `owned`, `missing`, `talismans`, `trinkets`), active passive bonuses, and rare Talisman ingredients in Arthur's satchel. |
| `rdr2_capture_screen` | Captures a live PNG screenshot of the running RDR2 window (saved to `~/.rdr2_mcp/captures` by default). |
| `rdr2_send_input` | Sends an in-game key action (`whistle`, `calm`, `brush`, `dead_eye`, `map`, `journal`, `satchel`, etc.) via Win32 window messages. |
| `rdr2_set_waypoint` | Sets an in-game GPS Multi-Route waypoint to custom `(x, y)` coordinates or a named landmark. |
| `rdr2_encyclopedia` | Queries the offline database for `satchels`, `animals` (legendary), `camp` (upgrades), or `hunting` (weapon tiers). |

---

## 🤖 Install with an AI Agent (Copy-Paste Prompt)

Using **Google Antigravity**, **Claude Code**, **Cursor**, or another agentic IDE? Paste this prompt and let your AI set everything up automatically:

```text
Install and configure rdr2-mcp from https://github.com/wvzuilen/rdr2-mcp on my Windows PC for Red Dead Redemption 2 (Story Mode only):

1. Clone https://github.com/wvzuilen/rdr2-mcp.git into a clean local folder and install Python dependencies (`py -m pip install -r mcp_server/requirements.txt`).
2. Locate my Red Dead Redemption 2 installation directory and verify whether `ScriptHookRDR2.dll` and an ASI loader (`dinput8.dll`) are present (if missing, tell me where to download ScriptHookRDR2 from dev-c.com).
3. Build `mod_asi/src/main.cpp` into `RDR2_MCP_Bridge.asi` using either CMake + MSVC or a portable Zig C++ compiler (`zig c++ -target x86_64-windows-gnu -shared -O2 -DWIN32_LEAN_AND_MEAN -D_CRT_SECURE_NO_WARNINGS -o mod_asi/build/RDR2_MCP_Bridge.asi mod_asi/src/main.cpp -lws2_32 -luser32`), and copy `RDR2_MCP_Bridge.asi` into my RDR2 game root directory.
4. Add the `rdr2` MCP server entry pointing to my local `mcp_server/server.py` in my MCP client configuration file.
5. Verify all Python modules compile cleanly (`py -m py_compile mcp_server/*.py`) and test `rdr2_status` once the MCP server is reloaded.
```

---

## 🚀 Manual Quick Start

### 1. Requirements
* Windows 10 / 11 (64-bit)
* Python 3.10+
* Red Dead Redemption 2 PC (Story Mode)
* Optional (for full native telemetry, trackers & GPS waypoints):
  * [ScriptHookRDR2](http://www.dev-c.com/rdr2/scripthookrdr2/) (`ScriptHookRDR2.dll` + ASI loader such as `dinput8.dll`)
  * Either **CMake + MSVC (Visual Studio Build Tools)** *or* portable **[Zig 0.13+](https://ziglang.org/download/)** (~50 MB, no Visual Studio install required) to compile `RDR2_MCP_Bridge.asi`

### 2. Installation
Clone the repository and install Python dependencies:
```bash
git clone https://github.com/wvzuilen/rdr2-mcp.git
cd rdr2-mcp
py -m pip install -r mcp_server/requirements.txt
```

### 3. Building `RDR2_MCP_Bridge.asi` from Source (Recommended)
`mod_asi` requires **zero external ScriptHook SDK headers** — `RDR2_MCP_Bridge.asi` resolves `ScriptHookRDR2.dll` exports dynamically at runtime via `GetProcAddress`.

**Option A — Portable Zig C++ (fastest, single command, no Visual Studio needed):**
```powershell
mkdir mod_asi\build -Force
zig c++ -target x86_64-windows-gnu -shared -O2 -DWIN32_LEAN_AND_MEAN -D_CRT_SECURE_NO_WARNINGS `
  -o mod_asi\build\RDR2_MCP_Bridge.asi mod_asi\src\main.cpp -lws2_32 -luser32
```

**Option B — CMake + Visual Studio (MSVC):**
```powershell
cmake -S mod_asi -B mod_asi/build -A x64
cmake --build mod_asi/build --config Release
```

Copy the resulting `RDR2_MCP_Bridge.asi` into your Red Dead Redemption 2 root directory alongside `ScriptHookRDR2.dll` and your ASI loader (`dinput8.dll`).

> [!NOTE]
> `RDR2_MCP_Bridge.asi` exports its shared telemetry/waypoint symbols (`g_json_buf`, `g_pending_wp`, `g_wp_x`, `g_wp_y`, `g_wp_z`) in the PE Export Table, and `mcp_server/bridge.py` resolves their RVAs automatically at runtime. This works across any compiler (MSVC, Zig, MinGW, Clang) with zero manual offset updates.

### 4. Adding to Antigravity / Claude Desktop / MCP Clients

Add the following to your MCP client configuration (see [client_config/](client_config/) for templates, e.g. `~/.gemini/config/mcp_config.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "rdr2": {
      "command": "py",
      "args": [
        "C:\\path\\to\\rdr2-mcp\\mcp_server\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 💬 Example Prompts

Once connected while playing RDR2 Story Mode, you can ask your AI co-pilot things like:

* *"Where am I right now, and set a waypoint to the nearest Trapper."*
* *"Check my Master Hunter challenge progress and guide me to the closest bear spawn."*
* *"Which Camp Ledger upgrades am I still missing and how much will they cost?"*
* *"Check my Trinkets & Talismans — do I already have the rare jewelry needed to craft any Talismans at the Fence?"*
* *"Take a screenshot and tell me which direction the Post Office is from where Arthur is standing."*

---

## 🔧 Troubleshooting

* **`bridge_mode` shows `process_win32` instead of `native_scripthook_memory`:** Make sure `RDR2_MCP_Bridge.asi`, `ScriptHookRDR2.dll`, and your ASI loader (`dinput8.dll`) are in the RDR2 root directory, then restart RDR2.
* **Updated `RDR2_MCP_Bridge.asi` doesn't show new fields yet:** Windows keeps the old `.asi` loaded in memory until `RDR2.exe` is restarted. Restart RDR2 (and reload your MCP client if new tools were added to `server.py`).
* **GPS waypoint disappears after Fast Travel or a train ride:** RDR2 automatically clears active GPS routes on fast travel / loading screens — just ask your AI to set the waypoint again once you arrive.

---

## 📜 License & Disclaimer
This project is licensed under the [MIT License](LICENSE).  
*Red Dead Redemption 2* is a trademark of Rockstar Games / Take-Two Interactive. This project is an independent, non-commercial community tool intended solely for single-player Story Mode experimentation and accessibility, and is not affiliated with or endorsed by Rockstar Games.
