#!/usr/bin/env python3
# peon-ping-windsurf uninstaller
# Removes peon hooks from Windsurf hooks.json and cleans up state.

import json
import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PEON_SCRIPT = os.path.join(REPO_DIR, "peon.py")
HOOKS_FILE = os.path.join(os.path.expanduser("~"), ".codeium", "windsurf", "hooks.json")


def is_peon_hook(entry):
    cmd = entry.get("command", "")
    return PEON_SCRIPT in cmd or "peon.py" in cmd


def main():
    hooks_file = HOOKS_FILE

    print("peon-ping-windsurf uninstaller")
    print("==============================")
    print()

    # --- Remove hooks from hooks.json ---
    if os.path.isfile(hooks_file):
        try:
            with open(hooks_file) as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            print("✓ No valid hooks.json found, nothing to clean up")
            return

        hooks = config.get("hooks", {})
        changed = False

        for event in list(hooks.keys()):
            before = len(hooks[event])
            hooks[event] = [h for h in hooks[event] if not is_peon_hook(h)]
            if len(hooks[event]) != before:
                changed = True
            if not hooks[event]:
                del hooks[event]

        if changed:
            with open(hooks_file, "w") as f:
                json.dump(config, f, indent=2)
                f.write("\n")
            print(f"✓ Removed peon hooks from {hooks_file}")
        else:
            print(f"✓ No peon hooks found in {hooks_file}")
    else:
        print(f"✓ No hooks.json found at {hooks_file}, nothing to clean up")

    # --- Clean up state file ---
    state_file = os.path.join(REPO_DIR, ".state.json")
    if os.path.isfile(state_file):
        os.remove(state_file)
        print("✓ Removed state file")

    print()
    print("Done! Restart Windsurf (or reload the window) to deactivate.")
    print()
    print(f"The repo is still at {REPO_DIR} — delete it manually if you no longer need it:")
    print(f"  rm -rf {REPO_DIR}")


if __name__ == "__main__":
    main()
