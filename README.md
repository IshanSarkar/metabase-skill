# Metabase skill for any AI agent

An [Agent Skill](https://agentskills.io/specification) that answers Metabase questions from a local copy of the official Metabase docs. Author: Ishan Sarkar. Implementation: Cursor AI agent. Attribution: [CREDITS.md](CREDITS.md).

**OS:** macOS, Linux, Windows. The skill is files + Python stdlib — no Docker, no native binaries.

**Agents:** Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, OpenCode, and any client that loads `SKILL.md`.

After install, start a new chat and ask in plain language. You do not need a slash command.

```
How do I give each customer only their own rows?
Embed a chart in our React app without making them log into Metabase.
SQL dropdown that lists product categories.
```

## Install (pick one)

### Anyone, any OS, any agent — Skills CLI

Needs [Node.js](https://nodejs.org/). Same command on macOS, Linux, and Windows:

```bash
npx skills add IshanSarkar/metabase-skill -g -y
```

Add `-a cursor -a claude-code -a codex` to target specific products.

From a local clone:

```bash
npx skills add . -g -y
```

### Python installer (no Node)

Needs Python 3.9+. Same on every OS:

```bash
# macOS / Linux
python3 scripts/install.py

# Windows (PowerShell or cmd)
py -3 scripts\install.py
```

Flags: `--project` (current repo only), `--agent cursor` (one product).

Unix shortcut: `./install.sh` (calls the same Python installer).

### Cursor only — clone into the skills folder

| OS | Folder |
|----|--------|
| macOS / Linux | `~/.cursor/skills/metabase` |
| Windows | `%USERPROFILE%\.cursor\skills\metabase` |

```bash
git clone https://github.com/IshanSarkar/metabase-skill.git ~/.cursor/skills/metabase
```

Windows PowerShell:

```powershell
git clone https://github.com/IshanSarkar/metabase-skill.git "$env:USERPROFILE\.cursor\skills\metabase"
```

Then start a **new** Agent chat.

## Requirements

- **Python 3.9+** for lookup (standard library only: `pathlib`, `json`, `re`)
- Optional: **git** if `source/` is missing (first lookup clones Metabase `docs/`)
- Optional: **Node.js** only if you install via `npx skills add`

| OS | Python command |
|----|----------------|
| macOS / Linux | `python3` |
| Windows | `py -3` or `python` |

## How to use it in conversation

1. Install the skill.
2. Open a **new** agent thread (so the skill is discovered).
3. Ask a Metabase question in your own words.

The agent should run `scripts/lookup.py`, read the few PRIMARY pages, and answer with official doc links. If it does not, say: `Use the metabase skill` or `/metabase` where your client supports slash skills.

## Layout

```
SKILL.md                 # router (small — loaded when the skill fires)
scripts/lookup.py        # run this; do not paste it into context
scripts/install.py       # cross-platform installer
graph/concepts.json      # slang → official Metabase concepts
source/                  # official docs snapshot
references/              # short topic cheat sheets
install.sh               # Unix wrapper around scripts/install.py
```

## Credits

See [CREDITS.md](CREDITS.md).

- **Documentation source:** [Metabase documentation](https://www.metabase.com/docs/latest/) and the `docs/` folder of [metabase/metabase](https://github.com/metabase/metabase)
- **Docs snapshot:** 2026-09-10; latest Metabase at that time: **63.17** (`v0.63.17` OSS, `v1.63.17` Pro/Enterprise)
- **Author:** Ishan Sarkar
- **Implementation:** Cursor AI agent

This skill is not affiliated with or endorsed by Metabase, Inc.

## License

Skill packaging: MIT (`LICENSE`), Copyright © 2026 Ishan Sarkar.  
`source/` is Metabase documentation (AGPL); see `NOTICE.md`.
