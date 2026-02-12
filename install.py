#!/usr/bin/env python3
# peon-ping-windsurf installer
# Run from the cloned repo: python3 install.py

import json
import os
import stat
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PEON_SCRIPT = os.path.join(REPO_DIR, "peon.py")
HOOKS_FILE = os.path.join(os.path.expanduser("~"), ".codeium", "windsurf", "hooks.json")


def main():
    hooks_file = HOOKS_FILE

    print("peon-ping-windsurf installer")
    print("============================")
    print()
    print(f"Repo directory: {REPO_DIR}")
    print(f"Hooks file:     {hooks_file}")
    print()

    # --- Make peon.py executable ---
    st = os.stat(PEON_SCRIPT)
    os.chmod(PEON_SCRIPT, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("✓ Made peon.py executable")

    # --- Create hooks directory if needed ---
    os.makedirs(os.path.dirname(hooks_file), exist_ok=True)

    # --- Generate hooks from config.json ---
    config_file = os.path.join(REPO_DIR, "config.json")
    with open(config_file) as f:
        peon_cfg = json.load(f)
    peon_hooks = {}
    for hook_name in peon_cfg.get("hooks", {}):
        peon_hooks[hook_name] = [
            {"command": f"python3 {PEON_SCRIPT} --hook {hook_name}", "show_output": False}
        ]

    # --- Load existing hooks.json or start fresh ---
    if os.path.isfile(hooks_file):
        try:
            with open(hooks_file) as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    hooks = config.setdefault("hooks", {})

    # --- Merge peon hooks into existing config ---
    for event, entries in peon_hooks.items():
        hook_list = hooks.setdefault(event, [])
        # Remove any existing peon-ping-windsurf entries
        hook_list[:] = [h for h in hook_list if "peon.py" not in h.get("command", "")]
        hook_list.extend(entries)

    with open(hooks_file, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"✓ Hooks written to {hooks_file}")
    print()
    print("Done! Restart Windsurf (or reload the window) to activate.")
    print()
    print("To uninstall later, run:")
    print(f"  python3 {os.path.join(REPO_DIR, 'uninstall.py')}")


if __name__ == "__main__":
    main()
