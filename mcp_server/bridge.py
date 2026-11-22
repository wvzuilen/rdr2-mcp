"""
RDR2 Live Telemetry Bridge
Connects to a running Red Dead Redemption 2 instance via:
1. ScriptHook HTTP Telemetry (when RDR2_MCP_Bridge.asi is active on localhost:28999)
2. Windows Process & Window Manager (Win32 API fallback for live capture, status, and input injection)
"""

import os
import sys
import math
import time
import json
import struct
import ctypes
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


DEFAULT_HTTP_PORT = 28999
RDR2_PROCESS_NAME = "RDR2.exe"
RDR2_WINDOW_TITLE = "Red Dead Redemption 2"

STATE_NAMES: Dict[int, str] = {
    0xF2D2E4A4: "Ambarino",
    0x00A55D60: "Lemoyne",
    0xB32957A3: "New Hanover",
    0x4A4BFEE7: "West Elizabeth",
    0xB5AA074D: "Upper West Elizabeth",
    0x8A606F74: "Lower West Elizabeth",
    0x79E6A26B: "New Austin",
}

TOWN_NAMES: Dict[int, str] = {
    0x1B6880B3: "Valentine",
    0x197DEE02: "Strawberry",
    0xE3CDCF62: "Emerald Ranch",
    0x79FF6291: "Rhodes",
    0xD25EC74F: "Saint Denis",
    0x00704B67: "Annesburg",
    0x7EBD16BD: "Van Horn",
    0x3EC4B1F5: "Blackwater",
    0xCBFCD82E: "Wallace Station",
    0x91A7512E: "Cornwall Kerosene & Tar",
}

DISTRICT_NAMES: Dict[int, str] = {
    0x07D4FF5F: "The Heartlands",
    0x3108C492: "Big Valley",
    0x6D67801E: "Cumberland Forest",
    0x62162401: "Grizzlies West",
    0xF8D68DC1: "Grizzlies East",
    0xCC7C3314: "Scarlett Meadows",
    0x78BFE1AC: "Bayou Nwa",
    0x4DFA0B50: "Bluewater Marsh",
    0x0AA5F25D: "Roanoke Ridge",
    0x6467EF09: "Tall Trees",
    0x1C68EA97: "Great Plains",
}

WEAPON_HASH_FALLBACK: Dict[str, str] = {
    "0xF6687C5A": "Binoculars",
}

LANDMARKS: Dict[str, Dict[str, Any]] = {
    "horseshoe overlook": {"name": "Horseshoe Overlook", "x": -100.0, "y": -40.0, "z": 95.0, "region": "The Heartlands"},
    "calibans seat": {"name": "Caliban's Seat (Jack Hall Map 1 Treasure)", "x": -175.0, "y": 360.0, "z": 115.0, "region": "The Heartlands"},
    "cotorra springs": {"name": "Cotorra Springs (Jack Hall Map 2 Treasure)", "x": 240.46, "y": 1968.31, "z": 206.57, "region": "Grizzlies East"},
    "ocreaghs run island": {"name": "O'Creagh's Run Island (Jack Hall Map 3 - 2 Gold Bars)", "x": 1822.5, "y": 1690.4, "z": 252.1, "region": "Grizzlies East"},
    "cairn lake cabin": {"name": "Cairn Lake Cabin (Poisonous Trail Map 1)", "x": -1329.0, "y": 2407.0, "z": 310.5, "region": "Grizzlies West"},
    "face rock": {"name": "Face Rock (Poisonous Trail Map 2)", "x": 1075.0, "y": -655.0, "z": 82.0, "region": "Scarlett Meadows"},
    "valentine": {"name": "Valentine", "x": -180.0, "y": 600.0, "z": 110.0, "region": "The Heartlands"},
    "limpany": {"name": "Limpany", "x": -350.0, "y": -220.0, "z": 80.0, "region": "The Heartlands"},
    "emerald ranch": {"name": "Emerald Ranch", "x": 1200.0, "y": 250.0, "z": 85.0, "region": "The Heartlands"},
    "emerald ranch fence": {"name": "Emerald Ranch Fence (Seamus)", "x": 1417.82, "y": 268.03, "z": 89.62, "region": "The Heartlands"},
    "lake isabella": {"name": "Lake Isabella", "x": -1400.0, "y": 1400.0, "z": 300.0, "region": "Grizzlies West"},
    "strawberry": {"name": "Strawberry", "x": -1750.0, "y": -400.0, "z": 160.0, "region": "Big Valley"},
    "rhodes": {"name": "Rhodes", "x": 1250.0, "y": -1300.0, "z": 70.0, "region": "Scarlett Meadows"},
    "rhodes fence": {"name": "Rhodes Fence", "x": 1322.80, "y": -1142.75, "z": 81.80, "region": "Scarlett Meadows"},
    "rhodes gunsmith": {"name": "Rhodes Gunsmith (Free Lancaster Repeater)", "x": 1328.0, "y": -1322.0, "z": 77.8, "region": "Scarlett Meadows"},
    "legendary fox": {"name": "Legendary Fox (Mattock Pond East Slope)", "x": 1345.0, "y": -1035.0, "z": 76.0, "region": "Scarlett Meadows"},
    "bolger glade": {"name": "Bolger Glade", "x": 1365.0, "y": -1870.0, "z": 62.0, "region": "Scarlett Meadows"},
    "old harry fen panther": {"name": "Old Harry Fen Panther Woods", "x": 1418.0, "y": -2135.0, "z": 52.0, "region": "Scarlett Meadows"},
    "panther": {"name": "Old Harry Fen Panther Woods", "x": 1418.0, "y": -2135.0, "z": 52.0, "region": "Scarlett Meadows"},
    "iguana island": {"name": "Iguana Island Crossing (Clemens Point)", "x": 685.0, "y": -1260.0, "z": 42.5, "region": "Scarlett Meadows"},
    "saint denis": {"name": "Saint Denis", "x": 2500.0, "y": -1200.0, "z": 45.0, "region": "Bayou Nwa"},
    "saint denis fence": {"name": "Saint Denis Fence", "x": 2849.29, "y": -1203.05, "z": 47.69, "region": "Bayou Nwa"},
    "saint denis trapper": {"name": "Saint Denis Trapper", "x": 2831.33, "y": -1227.62, "z": 47.65, "region": "Bayou Nwa"},
    "van horn fence": {"name": "Van Horn Fence", "x": 2983.45, "y": 430.15, "z": 51.18, "region": "Roanoke Ridge"},
    "big valley trapper": {"name": "Big Valley Trapper", "x": -2838.72, "y": 130.93, "z": 184.12, "region": "Big Valley"},
    "big valley cougar": {"name": "Big Valley Cougar Spawn", "x": -2750.0, "y": -50.0, "z": 155.0, "region": "Big Valley"},
    "lake owanjila": {"name": "Lake Owanjila (Beaver Shore)", "x": -2615.0, "y": -385.0, "z": 147.0, "region": "Big Valley"},
    "beaver": {"name": "Lake Owanjila (Beaver Shore)", "x": -2615.0, "y": -385.0, "z": 147.0, "region": "Big Valley"},
    "riggs station trapper": {"name": "Riggs Station Trapper", "x": -1325.0, "y": -1275.0, "z": 120.0, "region": "Big Valley"},
    "roanoke ridge trapper": {"name": "Roanoke Ridge Trapper", "x": 2340.0, "y": 1580.0, "z": 200.0, "region": "Roanoke Ridge"},
    "annesburg cougar": {"name": "Annesburg North Cougar Spawn", "x": 2880.0, "y": 1620.0, "z": 102.0, "region": "Roanoke Ridge"},
    "tall trees trapper": {"name": "Tall Trees Trapper", "x": -1990.0, "y": -1860.0, "z": 75.0, "region": "Tall Trees"},
    "clear": {"name": "Clear Waypoint", "x": 0.0, "y": 0.0, "z": 0.0, "region": "None"},
    "off": {"name": "Clear Waypoint", "x": 0.0, "y": 0.0, "z": 0.0, "region": "None"},
}

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

_k32_mem = ctypes.WinDLL("kernel32", use_last_error=True)
_k32_mem.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
_k32_mem.OpenProcess.restype = ctypes.c_void_p
_k32_mem.CloseHandle.argtypes = [ctypes.c_void_p]
_k32_mem.CloseHandle.restype = ctypes.c_int
_k32_mem.ReadProcessMemory.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
]
_k32_mem.ReadProcessMemory.restype = ctypes.c_int
_k32_mem.WriteProcessMemory.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
]
_k32_mem.WriteProcessMemory.restype = ctypes.c_int
_k32_mem.CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
_k32_mem.CreateToolhelp32Snapshot.restype = ctypes.c_void_p

ASI_MODULE_NAME = "rdr2_mcp_bridge.asi"
ASI_DEFAULT_BASE = 0x6F360000
ASI_RVA_JSON_BUF = 0x9010
ASI_RVA_WP_X = 0x11164
ASI_RVA_WP_Y = 0x11168
ASI_RVA_PENDING_WP = 0x11170
ASI_RVA_WP_Z = 0x11174


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("th32ModuleID", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("GlblcntUsage", ctypes.c_ulong),
        ("ProccntUsage", ctypes.c_ulong),
        ("modBaseAddr", ctypes.c_void_p),
        ("modBaseSize", ctypes.c_ulong),
        ("hModule", ctypes.c_void_p),
        ("szModule", ctypes.c_wchar * 256),
        ("szExePath", ctypes.c_wchar * 260),
    ]


_k32_mem.Module32FirstW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MODULEENTRY32W)]
_k32_mem.Module32FirstW.restype = ctypes.c_int
_k32_mem.Module32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MODULEENTRY32W)]
_k32_mem.Module32NextW.restype = ctypes.c_int


def _decode_zone_hash(hash_val: Any, mapping: Dict[int, str]) -> Optional[str]:
    """Decode a 32-bit unsigned RDR2 zone hash into a readable name."""
    if not hash_val:
        return None
    try:
        h = int(hash_val, 16) if isinstance(hash_val, str) else int(hash_val)
    except (ValueError, TypeError):
        return str(hash_val)
    if h == 0:
        return None
    return mapping.get(h, f"0x{h:08X}")


def _nearest_landmark(x: float, y: float) -> Optional[Dict[str, Any]]:
    """Find the closest named RDR2 landmark using Euclidean XY distance."""
    best_key = None
    best_dist = float("inf")
    for key, lm in LANDMARKS.items():
        if lm["x"] == 0.0 and lm["y"] == 0.0:
            continue
        dist = math.hypot(x - lm["x"], y - lm["y"])
        if dist < best_dist:
            best_dist = dist
            best_key = key
    if best_key is None:
        return None
    lm = LANDMARKS[best_key]
    return {
        "key": best_key,
        "name": lm["name"],
        "region": lm["region"],
        "distance_m": round(best_dist, 1),
    }


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


class RDR2Bridge:
    def __init__(self, port: int = DEFAULT_HTTP_PORT):
        self.port = port
        self.http_url = f"http://127.0.0.1:{self.port}"
        self.last_known_pid = None
        self.last_known_hwnd = None
        self._rva_cache: Dict[Tuple[int, int], Dict[str, int]] = {}

    def _read_proc_bytes(self, h_proc: Any, addr: int, size: int) -> Optional[bytes]:
        buf = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t(0)
        ok = _k32_mem.ReadProcessMemory(
            h_proc,
            ctypes.c_void_p(addr),
            buf,
            size,
            ctypes.byref(bytes_read),
        )
        if not ok or bytes_read.value < size:
            return None
        return buf.raw[:size]

    def _resolve_bridge_rvas(self, h_proc: Any, pid: int, base: int) -> Dict[str, int]:
        """Resolve exported symbol RVAs from the loaded RDR2_MCP_Bridge.asi PE Export Directory,
        falling back to legacy hardcoded RVAs for older pre-export builds."""
        cache_key = (pid, base)
        if cache_key in self._rva_cache:
            return self._rva_cache[cache_key]

        rvas = {
            "g_json_buf": ASI_RVA_JSON_BUF,
            "g_wp_x": ASI_RVA_WP_X,
            "g_wp_y": ASI_RVA_WP_Y,
            "g_wp_z": ASI_RVA_WP_Z,
            "g_pending_wp": ASI_RVA_PENDING_WP,
        }
        try:
            hdr = self._read_proc_bytes(h_proc, base, 0x1000)
            if hdr and hdr[:2] == b"MZ":
                pe_off = struct.unpack_from("<I", hdr, 0x3C)[0]
                if pe_off + 0x100 <= len(hdr) and hdr[pe_off:pe_off + 4] == b"PE\x00\x00":
                    opt_off = pe_off + 24
                    magic = struct.unpack_from("<H", hdr, opt_off)[0]
                    dd_off = opt_off + (112 if magic == 0x20B else 96)
                    exp_rva, exp_size = struct.unpack_from("<II", hdr, dd_off)
                    if exp_rva and exp_size:
                        exp_dir = self._read_proc_bytes(h_proc, base + exp_rva, 40)
                        if exp_dir:
                            num_names, = struct.unpack_from("<I", exp_dir, 24)
                            addr_rva, name_rva, ord_rva = struct.unpack_from("<III", exp_dir, 28)
                            if 0 < num_names <= 2048:
                                names_tbl = self._read_proc_bytes(h_proc, base + name_rva, num_names * 4)
                                ords_tbl = self._read_proc_bytes(h_proc, base + ord_rva, num_names * 2)
                                if names_tbl and ords_tbl:
                                    wanted = set(rvas.keys())
                                    found: Dict[str, int] = {}
                                    for i in range(num_names):
                                        nrva = struct.unpack_from("<I", names_tbl, i * 4)[0]
                                        raw_name = self._read_proc_bytes(h_proc, base + nrva, 32)
                                        if not raw_name:
                                            continue
                                        nul = raw_name.find(b"\x00")
                                        sym = (raw_name[:nul] if nul != -1 else raw_name).decode("ascii", errors="ignore")
                                        if sym in wanted:
                                            ord_idx = struct.unpack_from("<H", ords_tbl, i * 2)[0]
                                            frva_bytes = self._read_proc_bytes(h_proc, base + addr_rva + ord_idx * 4, 4)
                                            if frva_bytes:
                                                found[sym] = struct.unpack("<I", frva_bytes)[0]
                                    if found:
                                        rvas.update(found)
        except Exception:
            pass

        self._rva_cache[cache_key] = rvas
        return rvas

    def _enrich_telemetry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decode zone hashes, weapon fallback hashes, and nearest landmark."""
        player = data.get("player")
        world = data.get("world")
        if isinstance(player, dict):
            active_wep = player.get("active_weapon")
            if isinstance(active_wep, str) and active_wep in WEAPON_HASH_FALLBACK:
                player["active_weapon"] = WEAPON_HASH_FALLBACK[active_wep]
        if isinstance(world, dict):
            world["state"] = _decode_zone_hash(world.get("state_hash"), STATE_NAMES)
            world["town"] = _decode_zone_hash(world.get("town_hash"), TOWN_NAMES)
            world["district"] = _decode_zone_hash(world.get("district_hash"), DISTRICT_NAMES)
            coords = player.get("coords") if isinstance(player, dict) else None
            if isinstance(coords, dict) and "x" in coords and "y" in coords:
                world["nearest_landmark"] = _nearest_landmark(float(coords["x"]), float(coords["y"]))
                if isinstance(player, dict):
                    player["region"] = world["district"] or world["state"]
                    if world["town"]:
                        player["town"] = world["town"]
        return data

    def check_http_bridge(self) -> Optional[Dict[str, Any]]:
        """Attempt to query the native ScriptHook HTTP bridge."""
        try:
            req = urllib.request.Request(
                f"{self.http_url}/status",
                headers={"User-Agent": "RDR2-MCP/1.0"}
            )
            with urllib.request.urlopen(req, timeout=0.15) as response:
                if response.status == 200:
                    raw = response.read().decode("utf-8")
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        return self._enrich_telemetry(data)
                    return data
        except Exception:
            return None
        return None

    def _find_bridge_module_base(self, pid: int) -> int:
        """Locate RDR2_MCP_Bridge.asi base address in target process, or fall back to default."""
        TH32CS_SNAPMODULE = 0x00000008
        TH32CS_SNAPMODULE32 = 0x00000010
        h_snap = _k32_mem.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
        if not h_snap or h_snap == -1 or h_snap == ctypes.c_void_p(-1).value:
            return ASI_DEFAULT_BASE
        try:
            me = MODULEENTRY32W()
            me.dwSize = ctypes.sizeof(MODULEENTRY32W)
            if _k32_mem.Module32FirstW(h_snap, ctypes.byref(me)):
                while True:
                    if me.szModule.lower() == ASI_MODULE_NAME:
                        return int(me.modBaseAddr or ASI_DEFAULT_BASE)
                    if not _k32_mem.Module32NextW(h_snap, ctypes.byref(me)):
                        break
        finally:
            _k32_mem.CloseHandle(h_snap)
        return ASI_DEFAULT_BASE

    def check_memory_bridge(self, pid: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Read live ScriptHook telemetry directly from RDR2_MCP_Bridge.asi memory."""
        if not pid:
            proc = self.find_game_process()
            if not proc:
                return None
            pid = proc["pid"]

        PROCESS_VM_READ = 0x0010
        h_proc = _k32_mem.OpenProcess(PROCESS_VM_READ, 0, pid)
        if not h_proc:
            return None
        try:
            base = self._find_bridge_module_base(pid)
            rvas = self._resolve_bridge_rvas(h_proc, pid, base)
            buf = ctypes.create_string_buffer(16384)
            bytes_read = ctypes.c_size_t(0)
            ok = _k32_mem.ReadProcessMemory(
                h_proc,
                ctypes.c_void_p(base + rvas["g_json_buf"]),
                buf,
                16384,
                ctypes.byref(bytes_read),
            )
            if not ok or bytes_read.value == 0:
                return None
            raw_bytes = buf.raw
            nul = raw_bytes.find(b"\x00")
            if nul != -1:
                raw_bytes = raw_bytes[:nul]
            text = raw_bytes.decode("utf-8", errors="ignore").strip()
            if not text.startswith("{"):
                return None
            data = json.loads(text)
            if isinstance(data, dict) and data.get("bridge_active"):
                return self._enrich_telemetry(data)
        except Exception:
            return None
        finally:
            _k32_mem.CloseHandle(h_proc)
        return None

    def set_waypoint_memory(self, x: float, y: float, z: float = 0.0) -> Dict[str, Any]:
        """Write waypoint coordinates directly into RDR2_MCP_Bridge.asi memory."""
        proc = self.find_game_process()
        if not proc:
            return {"success": False, "error": "RDR2.exe process not running."}
        pid = proc["pid"]

        PROCESS_VM_OPERATION = 0x0008
        PROCESS_VM_READ = 0x0010
        PROCESS_VM_WRITE = 0x0020
        h_proc = _k32_mem.OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, 0, pid)
        if not h_proc:
            err = ctypes.get_last_error()
            return {"success": False, "error": f"OpenProcess failed (Win32 error {err})."}

        try:
            base = self._find_bridge_module_base(pid)
            rvas = self._resolve_bridge_rvas(h_proc, pid, base)
            written = ctypes.c_size_t(0)
            writes = [
                (base + rvas["g_wp_x"], struct.pack("<f", float(x))),
                (base + rvas["g_wp_y"], struct.pack("<f", float(y))),
                (base + rvas["g_wp_z"], struct.pack("<f", float(z))),
                (base + rvas["g_pending_wp"], struct.pack("<i", 1)),
            ]
            for addr, payload in writes:
                c_buf = ctypes.create_string_buffer(payload, len(payload))
                ok = _k32_mem.WriteProcessMemory(
                    h_proc,
                    ctypes.c_void_p(addr),
                    c_buf,
                    len(payload),
                    ctypes.byref(written),
                )
                if not ok or written.value != len(payload):
                    err = ctypes.get_last_error()
                    return {"success": False, "error": f"WriteProcessMemory failed at {hex(addr)} (Win32 error {err})."}

            # Verify ScriptMain picks up g_pending_wp (resets to 0) within ~0.5s
            consumed = False
            pending_buf = ctypes.create_string_buffer(4)
            bytes_read = ctypes.c_size_t(0)
            for _ in range(10):
                time.sleep(0.06)
                if _k32_mem.ReadProcessMemory(
                    h_proc,
                    ctypes.c_void_p(base + rvas["g_pending_wp"]),
                    pending_buf,
                    4,
                    ctypes.byref(bytes_read),
                ) and bytes_read.value == 4:
                    val = struct.unpack("<i", pending_buf.raw)[0]
                    if val == 0:
                        consumed = True
                        break

            return {
                "success": True,
                "module_base": hex(base),
                "consumed_by_script": consumed,
                "detail": "ScriptMain consumed waypoint" if consumed else "queued (waiting for script tick)",
            }
        finally:
            _k32_mem.CloseHandle(h_proc)

    def find_game_process(self) -> Optional[Dict[str, Any]]:
        """Locate RDR2.exe via Windows Toolhelp snapshot."""
        TH32CS_SNAPPROCESS = 0x00000002

        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_char * 260)
            ]

        h_snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snap == -1:
            return None

        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if not kernel32.Process32First(h_snap, ctypes.byref(pe)):
            kernel32.CloseHandle(h_snap)
            return None

        found_proc = None
        while True:
            exe_name = pe.szExeFile.decode("latin1", errors="ignore")
            if exe_name.lower() == RDR2_PROCESS_NAME.lower():
                found_proc = {
                    "pid": int(pe.th32ProcessID),
                    "name": exe_name,
                    "threads": int(pe.cntThreads)
                }
                break
            if not kernel32.Process32Next(h_snap, ctypes.byref(pe)):
                break

        kernel32.CloseHandle(h_snap)
        if found_proc:
            self.last_known_pid = found_proc["pid"]
        return found_proc

    def find_game_window(self) -> Optional[int]:
        """Find the main game window handle (HWND)."""
        hwnd = user32.FindWindowW(None, RDR2_WINDOW_TITLE)
        if hwnd and hwnd != 0:
            self.last_known_hwnd = hwnd
            return hwnd
        
        # Fallback enum windows if exact title differs
        target_hwnd = []
        target_pid = self.last_known_pid

        def enum_cb(h, _):
            if user32.IsWindowVisible(h):
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
                if target_pid and pid.value == target_pid:
                    target_hwnd.append(h)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if target_hwnd:
            self.last_known_hwnd = target_hwnd[0]
            return target_hwnd[0]
        return None

    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Get window client dimensions (left, top, width, height)."""
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            return (rect.left, rect.top, w, h)
        return None

    def get_full_status(self) -> Dict[str, Any]:
        """Aggregate all available status and telemetry."""
        proc = self.find_game_process()
        if not proc:
            return {
                "running": False,
                "message": "Red Dead Redemption 2 is not currently running.",
                "bridge_mode": "offline"
            }

        hwnd = self.find_game_window()
        rect = self.get_window_rect(hwnd) if hwnd else None

        # Check native HTTP bridge, then direct ASI memory bridge
        native_data = self.check_http_bridge()
        bridge_mode = "native_scripthook"
        if not native_data:
            native_data = self.check_memory_bridge(proc["pid"])
            if native_data:
                bridge_mode = "native_scripthook_memory"

        if native_data:
            return {
                "running": True,
                "bridge_mode": bridge_mode,
                "process": proc,
                "window": {
                    "hwnd": hwnd,
                    "resolution": f"{rect[2]}x{rect[3]}" if rect else "unknown"
                },
                "telemetry": native_data
            }

        # Fallback process bridge
        return {
            "running": True,
            "bridge_mode": "process_win32",
            "process": proc,
            "window": {
                "hwnd": hwnd,
                "title": RDR2_WINDOW_TITLE,
                "rect": {
                    "left": rect[0], "top": rect[1], "width": rect[2], "height": rect[3]
                } if rect else None
            },
            "note": "Native ScriptHook HTTP bridge not detected on port 28999; operating via Win32 process & screen telemetry."
        }

    def capture_screenshot(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Capture the running RDR2 game screen to a local PNG file."""
        hwnd = self.find_game_window()
        if not hwnd:
            return {"success": False, "error": "RDR2 game window not found."}

        rect = self.get_window_rect(hwnd)
        if not rect or rect[2] <= 0 or rect[3] <= 0:
            return {"success": False, "error": "Invalid window dimensions."}

        left, top, width, height = rect

        if not output_dir:
            output_dir = os.path.join(str(Path.home()), ".rdr2_mcp", "captures")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"rdr2_capture_{int(time.time())}.png"
        filepath = os.path.join(output_dir, filename)

        # Ensure game window is restored and foreground
        try:
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.keybd_event(0, 0, 0, 0)
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.4)
        except Exception:
            pass

        # Attempt capture via PIL/Pillow if installed
        try:
            from PIL import ImageGrab
            # Bounding box: left, top, right, bottom
            bbox = (left, top, left + width, top + height)
            img = ImageGrab.grab(bbox=bbox)
            img.save(filepath, "PNG")
            return {
                "success": True,
                "path": filepath,
                "filename": filename,
                "width": width,
                "height": height,
                "aspect_ratio": f"{width}:{height}"
            }
        except ImportError:
            pass

        # Fallback to PowerShell GDI capture
        ps_cmd = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $bmp = New-Object System.Drawing.Bitmap {width}, {height}
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen({left}, {top}, 0, 0, (New-Object System.Drawing.Size({width}, {height})))
        $bmp.Save('{filepath}', [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose()
        $bmp.Dispose()
        """
        import subprocess
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
        if os.path.exists(filepath):
            return {
                "success": True,
                "path": filepath,
                "filename": filename,
                "width": width,
                "height": height
            }

        return {"success": False, "error": f"Capture failed: {res.stderr.decode('utf-8', errors='ignore')}"}

    def send_game_action(self, action: str) -> Dict[str, Any]:
        """Inject virtual keyboard actions into the RDR2 game process."""
        # VK Codes
        VK_MAP = {
            "whistle": 0x48,     # H
            "calm": 0x47,        # G
            "brush": 0x42,       # B
            "dead_eye": 0x14,    # CapsLock
            "map": 0x4D,         # M
            "log": 0x4C,         # L
            "journal": 0x4A,     # J
            "satchel": 0x42,     # B
            "reload": 0x52,      # R
            "melee": 0x46,       # F
            "cover": 0x51,       # Q
            "mount": 0x45,       # E
            "hitch": 0x54,       # T
            "cinematic": 0x56,   # V
            "rampage": 0x74,     # F5
            "screenshot": 0x7B,  # F12
            "pause": 0x1B        # ESC
        }

        action_clean = action.lower().strip()
        vk_code = VK_MAP.get(action_clean)

        if not vk_code:
            return {
                "success": False,
                "error": f"Unknown action '{action}'. Supported actions: {list(VK_MAP.keys())}"
            }

        hwnd = self.find_game_window()
        if not hwnd:
            return {"success": False, "error": "RDR2 game window not found."}

        # Bring window to foreground
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.05)

        # Send WM_KEYDOWN and WM_KEYUP
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        user32.PostMessageW(hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.1)
        user32.PostMessageW(hwnd, WM_KEYUP, vk_code, 0)

        return {
            "success": True,
            "action": action_clean,
            "vk_code": hex(vk_code),
            "message": f"Successfully triggered '{action_clean}' in RDR2."
        }
