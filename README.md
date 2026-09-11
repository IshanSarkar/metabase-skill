# Metabase skill for any AI agent

An [Agent Skill](https://agentskills.io/specification) that answers Metabase questions from a local copy of the official docs, with a lookup script so the agent does not dump the entire handbook into context.

Works with **Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, OpenCode**, and other clients that load `SKILL.md`.

After install, start a new chat and ask in plain language. You do not need a slash command.

```
How do I give each customer only their own rows?
Embed a chart in our React app without making them log into Metabase.
SQL dropdown that lists product categories.
```

## Install (pick one)

### Anyone, any agent — Skills CLI

```bash
npx skills add <GITHUB_OWNER>/<REPO> -g -y
```

That copies the skill into each selected agent's user-level skills folder. Add `-a cursor -a claude-code -a codex` to target specific products.

Until the repo is on GitHub, install from a local clone:

```bash
git clone <this-repo-url> metabase-skill
cd metabase-skill
npx skills add . -g -y
# or
./install.sh
```

### Cursor (user-wide)

```bash
git clone <this-repo-url> ~/.cursor/skills/metabase
```

Restart Cursor or start a new Agent chat.

### Claude Code

```bash
git clone <this-repo-url> ~/.claude/skills/metabase
```

### Codex

```bash
git clone <this-repo-url> ~/.codex/skills/metabase
```

### This project only

```bash
./install.sh --project
```

Puts the skill in `.cursor/skills/metabase` and `.agents/skills/metabase` so teammates get it with the repo.

## Requirements

- Python 3.9+ (standard library only) for `scripts/lookup.py`
- Optional: `git` if `source/` is missing (first lookup clones Metabase `docs/`)

## How to use it in conversation

1. Install the skill.
2. Open a **new** agent thread (so the skill is discovered).
3. Ask a Metabase question in your own words.

The agent should run `scripts/lookup.py`, read the few PRIMARY pages, and answer with official doc links. If it does not, say: `Use the metabase skill` or `/metabase` where your client supports slash skills.

## Layout

```
SKILL.md                 # router (small — always loaded when the skill fires)
scripts/lookup.py        # run this; do not paste it into context
graph/concepts.json      # slang → official Metabase concepts
source/                  # official docs snapshot
references/              # short topic cheat sheets
install.sh               # copy into local agent skill folders
```

## License

Skill packaging: MIT (`LICENSE`).  
`source/` is Metabase documentation (AGPL); see `NOTICE.md`.
