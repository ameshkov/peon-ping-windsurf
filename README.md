# peon-ping-windsurf

![macOS](https://img.shields.io/badge/macOS-blue) ![Linux](https://img.shields.io/badge/Linux-blue) ![WSL2](https://img.shields.io/badge/WSL2-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Windsurf](https://img.shields.io/badge/Windsurf-Cascade_hook-ffab01)

**Your Peon pings you when Windsurf Cascade finishes working.**

A Windsurf-compatible port of
[peon-ping](https://github.com/tonyyont/peon-ping).
Plays Warcraft III Peon voice lines via Cascade hooks —
so your IDE sounds like Orgrimmar.

- [What you'll hear](#what-youll-hear)
- [Prerequisites](#prerequisites)
- [Install](#install)
- [Uninstall](#uninstall)
- [Configuration](#configuration)
- [Sound packs](#sound-packs)
- [How it works](#how-it-works)
- [Credits](#credits)
- [License](#license)

## What you'll hear

| Event | Sound | Examples |
| --- | --- | --- |
| Cascade finishes responding | Complete | *"Ready to work?"*, *"Work, work."*, *"Something need doing?"* |
| Cascade writes code | Acknowledge | *"I can do that."*, *"Okie dokie."*, *"Be happy to."* |
| Cascade runs a command | Acknowledge | *"OK."*, *"Work, work."* |
| Rapid prompts (3+ in 10s) | Easter egg | *"Me busy, leave me alone!"* |

> [!NOTE]
> Examples above are from the default Orc Peon pack.
> More [sound packs](#sound-packs) are available, including
> Human Peasant, Undead Acolyte, StarCraft, and
> Red Alert 2 characters.

## Prerequisites

- **OS**: macOS, Linux, or WSL2
- **Python 3**
- **Windsurf** with
  [Cascade hooks](https://docs.windsurf.com/windsurf/cascade/hooks)
  support
- **Audio playback tool** (one of the following,
  depending on your platform):
  - macOS — `afplay` (built-in)
  - Linux — `paplay` (PulseAudio/PipeWire),
    `aplay` (ALSA), `ffplay` (FFmpeg), or `mpv`
  - WSL2 — PowerShell `MediaPlayer`
    (uses Windows audio via `powershell.exe`)

## Install

```bash
git clone https://github.com/ameshkov/peon-ping-windsurf.git ~/.peon-ping-windsurf
python3 ~/.peon-ping-windsurf/install.py
```

The install script reads `config.json` to determine which
hooks to register, makes `peon.py` executable, and writes
the entries to `~/.codeium/windsurf/hooks.json` (creating
it if needed, merging with existing hooks).

Restart Windsurf (or reload the window) and sounds will
play automatically.

You can clone to any location — the script auto-detects
its own path. To add or remove hooks, edit `config.json`
and re-run `python3 install.py`.

### Manual setup

If you prefer to configure hooks manually, create or edit
`~/.codeium/windsurf/hooks.json` (user-level) or
`.windsurf/hooks.json` (workspace-level):

```json
{
  "hooks": {
    "post_cascade_response": [
      {
        "command": "python3 /path/to/peon.py --hook post_cascade_response",
        "show_output": false
      }
    ]
  }
}
```

## Uninstall

```bash
python3 ~/.peon-ping-windsurf/uninstall.py
```

Removes peon hooks from `~/.codeium/windsurf/hooks.json`
and cleans up state. The repo itself is left in place —
delete it manually if you no longer need it.

## Configuration

Edit `config.json` in the repo directory
(e.g. `~/.peon-ping-windsurf/config.json`):

```json
{
  "active_pack": "peon",
  "volume": 1,
  "enabled": true,
  "hooks": {
    "post_cascade_response": {
      "enabled": true,
      "categories": ["complete"]
    },
    "pre_user_prompt": {
      "enabled": true,
      "categories": ["greeting"]
    },
    "post_write_code": {
      "enabled": true,
      "categories": ["acknowledge"]
    },
    "post_run_command": {
      "enabled": true,
      "categories": ["acknowledge"]
    }
  },
  "annoyed_threshold": 3,
  "annoyed_window_seconds": 10
}
```

- **volume**: 0.0–1.0
- **enabled**: set to `false` to mute everything
- **active_pack**: which sound pack to use
- **hooks**: per-hook configuration:
  - **enabled**: set to `false` to disable a specific hook
  - **categories**: list of sound categories to randomly
    pick from when the hook fires
- **annoyed_threshold / annoyed_window_seconds**: how many
  prompts in N seconds triggers the easter egg

Available categories: `greeting`, `acknowledge`,
`complete`, `error`, `permission`, `resource_limit`,
`annoyed`.

The `annoyed` category is special — include it in a
hook's categories list and it will only trigger when rapid
prompts exceed the threshold. Otherwise a random
non-annoyed category from the list is used.

## Sound packs

| Pack | Character | By |
| --- | --- | --- |
| `peon` (default) | Orc Peon (Warcraft III) | [@tonyyont](https://github.com/tonyyont) |
| `peon_fr` | Orc Peon (French) | [@thomasKn](https://github.com/thomasKn) |
| `peon_pl` | Orc Peon (Polish) | [@askowronski](https://github.com/askowronski) |
| `peon_ru` | Orc Peon (Russian) | [@maksimfedin](https://github.com/maksimfedin) |
| `peasant` | Human Peasant (Warcraft III) | [@thomasKn](https://github.com/thomasKn) |
| `peasant_fr` | Human Peasant (French) | [@thomasKn](https://github.com/thomasKn) |
| `peasant_ru` | Human Peasant (Russian) | [@maksimfedin](https://github.com/maksimfedin) |
| `acolyte_ru` | Undead Acolyte (Russian) | [@maksimfedin](https://github.com/maksimfedin) |
| `ra2_soviet_engineer` | Soviet Engineer (Red Alert 2) | [@msukkari](https://github.com/msukkari) |
| `sc_battlecruiser` | Battlecruiser (StarCraft) | [@garysheng](https://github.com/garysheng) |
| `sc_kerrigan` | Sarah Kerrigan (StarCraft) | [@garysheng](https://github.com/garysheng) |

Switch packs by editing `config.json`:

```json
{ "active_pack": "sc_kerrigan" }
```

## How it works

`peon.py` is registered as a Windsurf Cascade hook. On each event it:

1. Reads the `--hook` argument to determine which
   hook fired
2. Looks up the hook in `config.json` to get the
   list of candidate categories
3. Picks a random category, then a random voice line
   from it (avoiding repeats)
4. Plays it via `afplay` (macOS),
   `paplay`/`aplay`/`ffplay`/`mpv` (Linux), or
   PowerShell `MediaPlayer` (WSL2)

Sound files are property of their respective publishers
(Blizzard Entertainment, EA) and are included for
convenience.

## Credits

Based on [peon-ping](https://github.com/tonyyont/peon-ping)
by [@tonyyont](https://github.com/tonyyont).

## License

[MIT](LICENSE)
