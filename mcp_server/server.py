#!/usr/bin/env python3
"""
RDR2 Model Context Protocol (MCP) Server
Standard JSON-RPC 2.0 stdio server providing live bridge tools for Red Dead Redemption 2.
"""

import sys
import json
import logging
from typing import Dict, Any, List

from bridge import RDR2Bridge, LANDMARKS
from encyclopedia import query_encyclopedia


# Set up logging to stderr (stdout is reserved for JSON-RPC messages)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [rdr2-mcp] %(message)s"
)
logger = logging.getLogger("rdr2-mcp")

bridge = RDR2Bridge()

# Tools definitions
TOOLS = [
    {
        "name": "rdr2_status",
        "description": "Checks the connection to Red Dead Redemption 2, active process info, and bridge mode.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_player_state",
        "description": "Retrieves Arthur Morgan's current live state: coordinates, region, nearest landmark, health/stamina/dead eye cores & ranks, cash balance, bounty, wanted level, weapons, ammo, and inventory.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_horse_state",
        "description": "Retrieves the active horse's telemetry (health, stamina, distance to Arthur, breed, bonding).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_world_info",
        "description": "Retrieves in-game environmental data (clock time, weather, active region/territory).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_capture_screen",
        "description": "Takes a live high-resolution screenshot directly from the running RDR2 game window.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_dir": {
                    "type": "string",
                    "description": "Optional custom directory path to save the PNG screenshot."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_send_input",
        "description": "Injects a direct game action into RDR2 (e.g., whistle for horse, dead eye, open map, reload, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to trigger: 'whistle', 'calm', 'brush', 'dead_eye', 'map', 'journal', 'satchel', 'reload', 'melee', 'cover', 'mount', 'hitch', 'cinematic', 'rampage', 'pause'.",
                    "enum": [
                        "whistle", "calm", "brush", "dead_eye", "map",
                        "journal", "satchel", "reload", "melee", "cover",
                        "mount", "hitch", "cinematic", "rampage", "pause"
                    ]
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_set_waypoint",
        "description": "Sets an in-game GPS waypoint to specific coordinates or named landmark.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "landmark": {
                    "type": "string",
                    "description": "Landmark name (e.g. 'Valentine', 'Horseshoe Overlook', 'Emerald Ranch Fence', 'Rhodes Fence', 'Saint Denis Fence', 'Van Horn Fence', 'Big Valley Trapper', 'Riggs Station Trapper', 'Saint Denis Trapper')."
                },
                "x": {"type": "number", "description": "World X coordinate."},
                "y": {"type": "number", "description": "World Y coordinate."}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "rdr2_encyclopedia",
        "description": "Queries the offline RDR2 database for hunting requirements (weapon tiers), Pearson satchel recipes, camp upgrades, or legendary animal trinkets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category to search: 'satchels', 'animals' (legendary), 'camp' (upgrades), or 'hunting' (weapon tiers).",
                    "enum": ["satchels", "animals", "camp", "hunting"]
                },
                "query": {
                    "type": "string",
                    "description": "Optional specific item or animal name to filter by (e.g. 'legend_of_the_east', 'buck', 'bear', 'fast travel', 'squirrel')."
                }
            },
            "required": ["category"],
            "additionalProperties": False
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool and return structured content."""
    logger.info(f"Tool call: {name} with args: {arguments}")

    if name == "rdr2_status":
        return bridge.get_full_status()

    elif name in ("rdr2_player_state", "rdr2_horse_state", "rdr2_world_info"):
        status = bridge.get_full_status()
        if not status.get("running"):
            return status

        telemetry = status.get("telemetry")
        section_map = {
            "rdr2_player_state": "player",
            "rdr2_horse_state": "horse",
            "rdr2_world_info": "world",
        }
        section = section_map[name]
        if telemetry and section in telemetry:
            data = telemetry[section]
            if name == "rdr2_player_state" and isinstance(data, dict):
                nearest = telemetry.get("world", {}).get("nearest_landmark")
                if nearest:
                    return {**data, "nearest_landmark": nearest}
            return data
        if telemetry:
            return telemetry

        return {
            "status": "Game is running",
            "mode": status["bridge_mode"],
            "process_id": status["process"]["pid"],
            "window": status.get("window", {}),
            "note": "Native telemetry bridge not active. For full live stats, ensure RDR2_MCP_Bridge.asi is in your game root."
        }

    elif name == "rdr2_capture_screen":
        out_dir = arguments.get("output_dir")
        return bridge.capture_screenshot(out_dir)

    elif name == "rdr2_send_input":
        action = arguments.get("action", "")
        return bridge.send_game_action(action)

    elif name == "rdr2_set_waypoint":
        landmark = arguments.get("landmark", "").lower().strip()
        coords = None
        if landmark in LANDMARKS:
            coords = LANDMARKS[landmark]
        elif "x" in arguments and "y" in arguments:
            coords = {"x": arguments["x"], "y": arguments["y"]}

        if not coords:
            return {
                "success": False,
                "error": f"Unknown landmark '{landmark}'. Known landmarks: {list(LANDMARKS.keys())} or provide x,y."
            }

        # Attempt to post to native bridge if present (single-packet HTTP POST)
        native_result = None
        try:
            import socket
            body = json.dumps({"x": coords["x"], "y": coords["y"], "z": coords.get("z", 0.0)}).encode("utf-8")
            raw_req = (
                f"POST /waypoint HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{bridge.port}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("ascii") + body
            with socket.create_connection(("127.0.0.1", bridge.port), timeout=0.15) as sock:
                sock.sendall(raw_req)
                resp_raw = sock.recv(4096).decode("utf-8", errors="ignore")
                if "200 OK" in resp_raw:
                    native_result = "Set directly via ScriptHook native bridge."
        except Exception:
            pass

        if native_result is None:
            mem_res = bridge.set_waypoint_memory(coords["x"], coords["y"], coords.get("z", 0.0))
            if mem_res.get("success"):
                native_result = f"Set via direct ScriptHook memory bridge ({mem_res.get('detail', 'ok')})."
            else:
                return {
                    "success": False,
                    "target": landmark or "Custom Coords",
                    "coords": coords,
                    "error": mem_res.get("error", "Native bridge unavailable.")
                }

        return {
            "success": True,
            "target": landmark or "Custom Coords",
            "coords": coords,
            "native_bridge": native_result
        }

    elif name == "rdr2_encyclopedia":
        category = arguments.get("category", "")
        query = arguments.get("query", "")
        return query_encyclopedia(category, query)

    raise ValueError(f"Unknown tool: {name}")


def main():
    logger.info("RDR2 MCP Server starting (stdio JSON-RPC)...")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            continue

        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params", {})

        # Handle MCP Handshake
        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "rdr2-mcp",
                        "version": "1.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            logger.info("Client handshake completed.")

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                tool_result = handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_result, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                logger.error(f"Error in tool '{tool_name}': {e}", exc_info=True)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif msg_id is not None:
            # Method not found
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
