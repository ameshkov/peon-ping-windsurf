#!/usr/bin/env python3
# peon-ping-windsurf: Warcraft III Peon voice lines for Windsurf Cascade hooks
# Sound-only — no notifications, no tab titles, no CLI controls

import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PEON_DIR = os.environ.get("WINDSURF_PEON_DIR", SCRIPT_DIR)
CONFIG = os.path.join(PEON_DIR, "config.json")
STATE = os.path.join(PEON_DIR, ".state.json")


def detect_platform():
    system = platform.system()
    if system == "Darwin":
        return "mac"
    if system == "Linux":
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except OSError:
            pass
        return "linux"
    return "unknown"


def play_sound(file_path, volume, plat):
    if plat == "mac":
        subprocess.Popen(
            ["afplay", "-v", str(volume), file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif plat == "linux":
        # PulseAudio/PipeWire (most common on modern distros)
        if shutil.which("paplay"):
            # paplay volume is 0–65536, map from 0.0–1.0
            pa_vol = str(int(volume * 65536))
            subprocess.Popen(
                ["paplay", "--volume", pa_vol, file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        # ALSA fallback
        elif shutil.which("aplay"):
            subprocess.Popen(
                ["aplay", "-q", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        # ffplay fallback
        elif shutil.which("ffplay"):
            subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-volume", str(int(volume * 100)), file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        # mpv fallback
        elif shutil.which("mpv"):
            subprocess.Popen(
                ["mpv", "--no-video", f"--volume={int(volume * 100)}", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    elif plat == "wsl":
        wpath = subprocess.check_output(["wslpath", "-w", file_path]).decode().strip()
        wpath = wpath.replace("\\", "/")
        ps_script = (
            "Add-Type -AssemblyName PresentationCore; "
            "$p = New-Object System.Windows.Media.MediaPlayer; "
            f"$p.Open([Uri]::new('file:///{wpath}')); "
            f"$p.Volume = {volume}; "
            "Start-Sleep -Milliseconds 200; "
            "$p.Play(); "
            "Start-Sleep -Seconds 3; "
            "$p.Close()"
        )
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def main():
    plat = detect_platform()

    # --- Load config ---
    try:
        with open(CONFIG) as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    if str(cfg.get("enabled", True)).lower() == "false":
        return

    volume = cfg.get("volume", 0.5)
    active_pack = cfg.get("active_pack", "peon")
    hooks_cfg = cfg.get("hooks", {})

    # --- Parse --hook from command line ---
    hook_name = ""
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--hook" and i < len(sys.argv) - 1:
            hook_name = sys.argv[i + 1]
            break

    if not hook_name:
        return

    # --- Look up hook configuration ---
    hook_cfg = hooks_cfg.get(hook_name, {})
    if str(hook_cfg.get("enabled", True)).lower() == "false":
        return

    hook_categories = hook_cfg.get("categories", [])
    if not hook_categories:
        return

    # --- Drain stdin (Windsurf sends JSON via stdin) ---
    try:
        sys.stdin.read()
    except Exception:
        pass

    # --- Load state ---
    try:
        with open(STATE) as f:
            state = json.load(f)
    except Exception:
        state = {}

    state_dirty = False

    # --- Special handling for "annoyed" category (rapid-prompt detection) ---
    if "annoyed" in hook_categories:
        annoyed_threshold = int(cfg.get("annoyed_threshold", 3))
        annoyed_window = float(cfg.get("annoyed_window_seconds", 10))
        now = time.time()
        ts = [t for t in state.get("prompt_timestamps", []) if now - t < annoyed_window]
        ts.append(now)
        state["prompt_timestamps"] = ts
        state_dirty = True
        if len(ts) >= annoyed_threshold:
            # Rapid prompts detected — force annoyed category
            hook_categories = ["annoyed"]
        else:
            # Not enough rapid prompts yet — remove annoyed from candidates
            hook_categories = [c for c in hook_categories if c != "annoyed"]
            if not hook_categories:
                # Only annoyed was configured and threshold not met — save state and exit
                os.makedirs(os.path.dirname(STATE) or ".", exist_ok=True)
                with open(STATE, "w") as f:
                    json.dump(state, f)
                return

    # --- Pick a random category from the hook's list ---
    category = random.choice(hook_categories)

    # --- Pick sound ---
    sound_file = ""
    if category:
        pack_dir = os.path.join(PEON_DIR, "packs", active_pack)
        try:
            with open(os.path.join(pack_dir, "manifest.json")) as f:
                manifest = json.load(f)
            sounds = manifest.get("categories", {}).get(category, {}).get("sounds", [])
            if sounds:
                last_played = state.get("last_played", {})
                last_file = last_played.get(category, "")
                candidates = sounds if len(sounds) <= 1 else [s for s in sounds if s["file"] != last_file]
                pick = random.choice(candidates)
                last_played[category] = pick["file"]
                state["last_played"] = last_played
                state_dirty = True
                sound_file = os.path.join(pack_dir, "sounds", pick["file"])
        except Exception:
            pass

    # --- Write state once ---
    if state_dirty:
        os.makedirs(os.path.dirname(STATE) or ".", exist_ok=True)
        with open(STATE, "w") as f:
            json.dump(state, f)

    # --- Play sound ---
    if sound_file and os.path.isfile(sound_file):
        play_sound(sound_file, volume, plat)


if __name__ == "__main__":
    main()
