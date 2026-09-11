---
name: metabase
description: >-
  Answers questions about Metabase using a local knowledge base built from the
  official docs (install, Docker/JAR, databases, questions, SQL parameters,
  dashboards, Data Studio, models, metrics, permissions, SSO, embedding SDK,
  Metabot, API, Cloud). Use whenever the user mentions Metabase, MBQL, Metabot,
  Metabase embedding, guest/static embeds, row-level security in Metabase, or
  Metabase Cloud vs self-hosting.
license: MIT
compatibility: Requires Python 3.9+ (stdlib only). Works with any Agent Skills client (Cursor, Claude Code, Codex, Copilot, Gemini CLI, OpenCode, and others).
metadata:
  version: "1.0.0"
  docs_snapshot: "2026-09-10"
---

# Metabase Knowledge Base

This skill's root is the directory that contains this `SKILL.md` file.
Official docs snapshot: `source/` (fetched on first lookup if missing).
Live docs: https://www.metabase.com/docs/latest/

## Mandatory retrieval (do not skip)

Never answer Metabase questions from this file or from memory.

From **this skill root** (the folder that contains `SKILL.md`), **run** — do not read — the lookup script:

```bash
python3 scripts/lookup.py "PASTE THE USER QUESTION"
```

If the current working directory is not the skill root, invoke the script by the path next to this file (`scripts/lookup.py`).

Then:

1. **Read** every `read_path` listed under PRIMARY (absolute paths printed by lookup).
2. Do **not** treat ALSO CHECK as required.
3. If `MISS_RISK: True` or PRIMARY does not mention a noun from the question, search `source/` from the skill root: `rg -i -n 'noun' source -g '*.md'`.
4. Still missing or version-specific → fetch `https://www.metabase.com/docs/latest/<path>`.
5. Cite that official URL. Flag OSS vs Pro/Enterprise.

Lookup expands slang (`sandbox` → row-and-column-security) and ranks exact concept pages over the rest of that family.

## Where the facts are

| Path | Role |
|------|------|
| `source/` | Complete Metabase docs. Relative path = URL after `/docs/latest/` |
| `references/` | Optional cheat sheet **after** lookup, never instead of `source/` |
| `graph/concepts.json` | Alias + intent graph used by lookup |
| `scripts/lookup.py` | Retrieval. Always **run**, never load into context |

Skip `source/embedding/sdk/api/snippets/` unless the user names an SDK prop.

## Plan gates (do not get wrong)

Row/column security, impersonation, DB routing, JWT/SAML/OIDC, full-app embedding, tenants, serialization: **Pro/Enterprise**. Guest embeds work on OSS. Public links bypass row-level security. Permissions: **most permissive group wins**; restrict **All Users** first.
