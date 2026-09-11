# Metabase AI & API Reference

## Plan matrix

| Feature | OSS/Starter | Pro/Enterprise | Cloud-only |
|---------|-------------|----------------|------------|
| Metabot (with own API key) | ✅ | ✅ | ✅ |
| Metabase AI service (managed) | ❌ | ❌ | ✅ (add-on) |
| MCP server | ✅ | ✅ | ✅ |
| Agent API | ✅ | ✅ | ✅ |
| AI usage controls (per-group limits) | ❌ | ✅ | ✅ |
| Agent-driven development (CLI + Remote Sync) | ❌ | ✅ | ✅ |
| JWT auth for Agent API | ❌ | ✅ | ✅ |

Connecting your own AI provider does **not** require a paid plan. Metabase AI service is Cloud add-on only.

## AI overview

Three AI integration paths:

1. **Metabot** — built-in agent for daily Metabase tasks; granular tool/usage controls.
2. **MCP server** — connect external AI clients (Claude, Cursor, etc.) to query/explore data.
3. **Agent-driven development** — coding agent + CLI creates content, versions as YAML via Remote Sync.

Docs: https://www.metabase.com/docs/latest/ai/overview

## Metabot

Built-in AI assistant (cmd/ctrl+e or icon). Scoped to viewer's data permissions.

**Capabilities:** NLQ → query builder charts, SQL generation/editing, chart analysis, error fixing, transform code, document charts, Slack integration.

**Limitations:** English prompts work best; conversation context is session-only (reset clears history); always verify AI output. Reuses existing questions when possible before creating new ones.

**Embedded:** `<metabase-metabot>` / `MetabotQuestion` / `useMetabot` — SSO modular embed only (Pro/Enterprise).

**Enable:** Admin > AI → connect provider → configure Metabot settings.

Docs: https://www.metabase.com/docs/latest/ai/metabot, https://www.metabase.com/docs/latest/embedding/ai-chat

## AI providers

Configure at **Admin > AI > Add a provider**. Self-hosted **must** bring own API key; Cloud can use Metabase AI service or BYOK.

| Provider key | Default model | Env var (API key) |
|-------------|---------------|-------------------|
| `anthropic` | claude-sonnet-4-6 | `MB_LLM_ANTHROPIC_API_KEY` |
| `openai` | gpt-5.4 | `MB_LLM_OPENAI_API_KEY` |
| `openrouter` | anthropic/claude-sonnet-4.6 | `MB_LLM_OPENROUTER_API_KEY` |
| `mistral` | mistral-medium-3-5 | `MB_LLM_MISTRAL_API_KEY` |
| `bedrock` | anthropic.claude-opus-4-8 | `MB_LLM_BEDROCK_*` |
| `azure` | deployment-based | `MB_LLM_AZURE_*` |
| `google` | google/gemini-3.5-flash | `MB_LLM_GOOGLE_*` |
| `deepseek`, `zai`, `moonshot`, `vllm`, `metabase`* | varies | `MB_LLM_{PROVIDER}_*` |

\*`metabase` = Cloud managed service (license token, once only). Providers power **Metabot only**, not MCP.

Docs: https://www.metabase.com/docs/latest/ai/providers, https://www.metabase.com/docs/latest/ai/settings

## Usage controls (Pro/Enterprise)

**Admin > AI > Usage controls**

### Feature access (per group/tenant group)

| Toggle | Effect |
|--------|--------|
| AI features | Master on/off (hides Metabot UI) |
| Chat and NLQ | Sidebar chat, natural language queries |
| SQL generation | Metabot writes/edits SQL |
| Other tools | Error fixing, chart analysis, etc. |

Unchecking SQL generation but leaving Chat on → Metabot tries query builder instead.

### Usage limits

- Limit by **token count** (millions) or **message count**.
- Reset: daily / weekly / monthly.
- **Instance limit** — total pool across all users.
- **Group limits** — per-person cap; multi-group users get **highest** limit (not cumulative).
- **Tenant group limits** — same as group limits.
- **Specific tenant limits** — aggregate pool shared by all users in one tenant (billing use case).

Docs: https://www.metabase.com/docs/latest/ai/usage-controls

## Privacy

| Context | What's sent externally |
|---------|----------------------|
| Metabase AI service | Prompts, metadata (table/field names), field value samples, derived chart metrics (not raw timeseries) |
| BYOK provider | Same as above, to your chosen provider |
| MCP server | **Query results** sent to MCP client (client's AI provider may also see them) |
| Feedback submission | Conversation context + prompts to Metabase company |

Query **results** are NOT sent to Metabase AI service or third-party providers for Metabot. MCP is different — results go to the client.

Docs: https://www.metabase.com/docs/latest/ai/privacy

## Agent API

REST API for headless agentic BI on Metabase semantic layer. **Versioned** (unlike main API). Powers MCP server.

**Enable:** Admin > AI > MCP (Agent API toggle).

**Capabilities:** Search tables/metrics, inspect fields, construct + execute queries. No MBQL required.

**Pagination:** max 200 rows/request; `POST /api/agent/v1/query` returns `continuation_token`.

**Auth methods:**

| Method | Header | Notes |
|--------|--------|-------|
| API key | `X-API-Key: mb_...` | Permissions = key's group; not user-scoped |
| Session | `X-Metabase-Session: {token}` | `POST /api/session` with username/password → `id` field |
| JWT | `Authorization: Bearer {jwt}` | Pro/Enterprise; claims: `iat` (<180s old), `email` (required), optional `first_name`, `last_name`, `groups` |

JWT → session exchange: `POST /auth/sso/to_session` (under `/auth`, not `/api`).

Reference: https://github.com/metabase/metabase/blob/master/src/metabase/agent_api/reference.md

Docs: https://www.metabase.com/docs/latest/ai/agent-api

## MCP server

Endpoint: `https://{instance}/api/metabase-mcp`

**Enable:** Admin > AI > MCP > toggle MCP server. Requires AI features enabled (provider not required).

**Auth:** OAuth 2.0 (Metabase embedded OAuth server). User approves connection; results scoped to their permissions. Authorization audit log at Admin > AI > MCP > Authorizations.

**Client provides the AI** — Metabot's configured provider is NOT used for MCP calls.

### Tools (grouped)

**Interactive:** `visualize_query`, `render_drill_through` (inline charts in supported clients).

**Read-only:** `search`, `construct_query`, `execute_query`, `query` (paged, 200/page, 2000 max), `read_resource` (metabase:// URIs).

**Write:** `create_*`, `update_*`, `execute_sql` (disable via `mcp-execute-sql-enabled`). Inline charts: Claude, Cursor/VS Code, ChatGPT. Connect: `claude mcp add --transport http metabase https://{instance}/api/metabase-mcp`. Localhost: set `MB_SITE_URL` to reachable URL.

Docs: https://www.metabase.com/docs/latest/ai/mcp

## REST API (general)

**Not versioned** — endpoints may change; use with caution for production integrations.

### Interactive documentation

On any running instance:
- **Swagger UI:** `https://{instance}/api/docs`
- **OpenAPI JSON:** `https://{instance}/api/docs/openapi.json`
- **Static reference:** bundled as `api.html` in docs repo (links to tag sections like `#tag/apiagent`, `#tag/apinotification`)

Source docs reference: https://www.metabase.com/docs/latest/api.html (path varies; live docs at `/api/docs` on instance).

### Authentication

| Method | How | Scope |
|--------|-----|-------|
| **Session token** | `POST /api/session` → `{ "username", "password" }` → use `id` as token | Individual user |
| | Header: `X-Metabase-Session: {token}` | |
| **API key** | Admin > Settings > Authentication > API Keys | Group permissions (not user-specific) |
| | Header: `X-API-Key: mb_...` | |
| | Pro/Enterprise self-hosted: also via config file | |
| **JWT** | `Authorization: Bearer {jwt}` or SSO flows | Pro/Enterprise |

API keys inherit group permissions; if group deleted, keys reassigned to All Users.

**Changelog:** https://www.metabase.com/docs/latest/developers-guide/api-changelog

Docs: https://www.metabase.com/docs/latest/people-and-groups/api-keys

### Common API uses

- Force database sync/scan
- Bulk permissions management
- Content creation/archiving
- Notification endpoints (`/api/notification` replaces legacy `/api/alert`)

## Metabase CLI (`mb`)

Command-line client driving Metabase API. For humans or AI agents.

**Install:** `npm install -g @metabase/cli` (Node 20.6+, Metabase ≥58; browser login needs ≥63).

**Auth:**
```bash
mb auth login --url https://metabase.example.com          # browser SSO/password
mb auth login --url https://instance --profile prod < api-key.txt  # CI/script
# or: export MB_API_KEY=mb_... (read by CLI on local machine, NOT server env var)
mb auth status
mb auth logout
```

Profiles for multiple instances: `--profile name` on any command.

**Pro/Enterprise features:** `git-sync` (Remote Sync), some command groups.

**Agent-driven dev (Pro/Enterprise):** dev instance + CLI + YAML (Representation Format) + Remote Sync → PR → prod pull. Docs: https://www.metabase.com/docs/latest/ai/agent-driven-development

Docs: https://www.metabase.com/docs/latest/installation-and-operation/metabase-cli

## Quick picks

In-app AI → Metabot embed (SSO). Ad-hoc from Claude/Cursor → MCP. Custom agentic app → Agent API. Bulk content → CLI + Remote Sync. Scripting → REST API (key/session). Explore → `{instance}/api/docs`.
