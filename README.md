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

**RDR2-MCP** is an open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) bridge that connects AI coding assistants and agents (like Google Antigravity, Claude Desktop, Cursor, and VS Code) directly to a live running session of **Red Dead Redemption 2** (PC Story Mode).

---

## 🌟 Features

* **⚡ Real-Time Player Telemetry:** Live query of Arthur's world coordinates (`x, y, z`), heading, region/town & nearest landmark, health/stamina/dead-eye cores & ranks, cash balance, bounty & wanted level, active & owned weapons (including ammo & arrow counts), and trinkets/tonics/herbs inventory.
* **🐴 Horse Tracking:** Monitor your active horse's spawn & mounted status, model hash, distance to Arthur, health/stamina cores & values, and bonding rank.
* **🗺️ World & Environment:** Read in-game clock time, ambient temperature (`°C`), active state/town/district names, and active waypoint status.
* **🧭 In-Game GPS Waypoints (`rdr2_set_waypoint`):** Programmatically place an in-game red GPS Multi-Route directly onto the minimap and world map using exact coordinates or built-in named landmarks (towns, Fences, Trappers, and notable locations).
* **🎮 In-Game Input & Live Screen Capture:** Send Win32 input actions (`whistle`, `calm`, `brush`, `dead_eye`, `map`, `journal`, `satchel`, etc.) and capture live screenshots of the game window as PNG files for visual analysis.
* **📖 Offline RDR2 Encyclopedia:** Instant lookup database for legendary animal locations & trinkets/talismans, hunting weapon tiers, Pearson satchel recipes, and camp upgrades.
* **🔌 Hybrid Dual Bridge Architecture:**
  1. **Native In-Game Bridge (`RDR2_MCP_Bridge.asi`):** ScriptHookRDR2 plugin exposing live native telemetry and GPS waypoint routing via both a direct Win32 memory fast-path (`ReadProcessMemory`/`WriteProcessMemory`) and an embedded local HTTP server (`http://127.0.0.1:28999`).
  2. **Non-Invasive Process Bridge (Fallback):** Automatically falls back to Windows Toolhelp process/window inspection and GDI/Win32 screen capture when the `.asi` bridge is not present.

---

## 🏛️ Architecture

```
+-----------------------------------------------------------------------------------+
|                           Red Dead Redemption 2 (PC)                              |
|                                                                                   |
|  [ RDR2_MCP_Bridge.asi (ScriptHookRDR2) ]          [ RDR2.exe Process & Window ]  |
|   HTTP Server (:28999) + Shared State RVA                GDI/Win32 Capture        |
+-----------------------------------------------------------------------------------+
                             ▲                                    ▲
                             │ HTTP / Win32 Memory                │ Win32 API
                             ▼                                    ▼
+-----------------------------------------------------------------------------------+
|                             rdr2-mcp Python Server                                |
|                                                                                   |
|  - Telemetry & Waypoint Bridge (Direct Memory / HTTP + Win32 Fallback)            |
|  - RDR2 Encyclopedia Engine (Hunting, Satchels, Trinkets, Camp Upgrades)          |
|  - Standard Model Context Protocol (MCP 2024-11-05 Stdio Transport)               |
+-----------------------------------------------------------------------------------+
                                         ▲
                                         │ JSON-RPC (stdio)
                                         ▼
+-----------------------------------------------------------------------------------+
|                             AI Assistant / Agent                                  |
|         (Google Antigravity, Claude Desktop, Cursor, Open WebUI)                  |
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
| `rdr2_capture_screen` | Captures a live PNG screenshot of the running RDR2 window (saved to `~/.rdr2_mcp/captures` by default). |
| `rdr2_send_input` | Sends an in-game key action (`whistle`, `calm`, `brush`, `dead_eye`, `map`, `journal`, `satchel`, etc.) via Win32 window messages. |
| `rdr2_set_waypoint` | Sets an in-game GPS Multi-Route waypoint to custom `(x, y)` coordinates or a named landmark. |
| `rdr2_encyclopedia` | Queries the offline database for `satchels`, `animals` (legendary), `camp` (upgrades), or `hunting` (weapon tiers). |

---

## 🚀 Quick Start

### 1. Requirements
* Windows 10 / 11 (64-bit)
* Python 3.10+
* Red Dead Redemption 2 PC (Story Mode)
* Optional (for full native telemetry & GPS waypoints): [ScriptHookRDR2](http://www.dev-c.com/rdr2/scripthookrdr2/) (`ScriptHookRDR2.dll` + ASI loader such as `dinput8.dll`) and Visual Studio Build Tools / MSVC + CMake to compile `RDR2_MCP_Bridge.asi`

### 2. Installation
Clone the repository and install Python dependencies:
```bash
git clone https://github.com/wvzuilen/rdr2-mcp.git
cd rdr2-mcp
py -m pip install -r mcp_server/requirements.txt
```

### 3. Building `RDR2_MCP_Bridge.asi` from Source (Recommended)
`mod_asi` requires **zero external ScriptHook SDK headers** — `RDR2_MCP_Bridge.asi` resolves `ScriptHookRDR2.dll` exports dynamically at runtime via `GetProcAddress`.

```powershell
cmake -S mod_asi -B mod_asi/build -A x64
cmake --build mod_asi/build --config Release
```

Copy the resulting `mod_asi/build/Release/RDR2_MCP_Bridge.asi` into your Red Dead Redemption 2 root directory alongside `ScriptHookRDR2.dll` and your ASI loader (`dinput8.dll`).

> [!NOTE]
> `mcp_server/bridge.py` supports both the local HTTP bridge (`http://127.0.0.1:28999`, compatible with any compiler/build) and an optional direct-memory fast-path (`ASI_RVA_*` offsets matching the reference MSVC Release build). If you recompile `main.cpp` with another compiler/settings and skip the HTTP path, update the `ASI_RVA_*` constants in `bridge.py` or rely on the HTTP bridge.

### 4. Adding to Antigravity / Claude Desktop / MCP Clients

Add the following to your MCP client configuration (see [client_config/](client_config/) for templates, e.g. `~/.gemini/config/mcp_config.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "rdr2": {
      "command": "py",
      "args": [
        "C:\\Users\\<YourUsername>\\Documents\\antigravity\\rdr2-mcp\\mcp_server\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 📜 License & Disclaimer
This project is licensed under the [MIT License](LICENSE).  
*Red Dead Redemption 2* is a trademark of Rockstar Games / Take-Two Interactive. This project is an independent, non-commercial community tool intended solely for single-player Story Mode experimentation and accessibility, and is not affiliated with or endorsed by Rockstar Games.
