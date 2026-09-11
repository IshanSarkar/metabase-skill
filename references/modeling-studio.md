# Metabase Data Modeling & Data Studio Reference

Official docs: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## Data modeling overview

**Models** — curated derived tables from same-database sources (query builder or SQL). Prefer **Transforms** for new work; models being phased out. Docs: `data-modeling/models`

- Rank higher in search; auto-pinned to collection on create
- SQL models need **Column type** (semantic type) set per column for query-builder exploration
- Refer in SQL: `{{#model-name}}` or CTE; breaking-change detection on save (**Pro/Enterprise**)
- **List view**: Settings tab → default view List; customize left/right columns
- **Search indexing**: string fields on records with integer entity keys (max 25k unique values)
- **Persistence** (deprecated): Postgres/MySQL/Redshift only; **incompatible with row/column security and impersonation**
- Convert model → transform (**Pro/Enterprise**): bulk via Data Studio > Transforms > Tools > Migrate models

**Metrics** — reusable aggregations on a specific data source. Docs: `data-modeling/metrics`

- Components: data source, formula (must be aggregation), dimensions (curated breakout/filter options)
- Formula: `SumIf`, `CountIf`, etc.; can reference other metrics; avoid filters in definition (use `*If` aggregations)
- Usable only on exact data source (not derived models/questions); query builder only (not SQL snippets)
- Permissions: Create/edit = not Blocked + Query builder+ + Curate collection; Use = not Blocked + Query builder+ + View collection
- Edit definition → all dependent questions update immediately
- **Pro/Enterprise**: verify, per-metric caching

**Segments** — saved filters. Prefer **Data Studio > Tables > Segments** over Admin > Table Metadata (legacy). Docs: `data-modeling/segments`, `data-studio/segments`

- Retiring segment does **not** break saved questions using it; edit triggers email to creators
- Only on primary table source (not joins/nested queries)

**Measures** (Data Studio) — table-scoped saved aggregations (older pattern; metrics are collection-scoped successor). Docs: `data-studio/measures`

- Create in Data Studio > Tables > Measures; delete doesn't break questions (reverts to unnamed aggregation)
- Only on primary table; not joins/nested queries

**Metadata editing** — Admin > Table Metadata (legacy) or Data Studio > Tables. Docs: `data-modeling/metadata-editing`, `data-studio/managing-tables`

- **Display-only** — does not change database data
- **Hidden tables/columns ≠ permissions** — SQL with table name still works; use data permissions to restrict
- Table: sync schema, scan/discard field values, visibility (eye icon), sort order
- Field: display name, description, semantic type, visibility (Everywhere / Detail only / Do not include), filtering widget (Search / Dropdown / Plain input), display values (FK remap, custom mapping), formatting
- **Dropdown filter**: needs Category semantic type + "list of all values"; scans first 1000 distinct values
- **Cast data types**: text→datetime, string→integer, etc. (not editable at DB level in Metabase)

**Semantic / field types** — Docs: `data-modeling/semantic-types`

- **Data type** (from DB sync): Numeric, Temporal, Text, Text-like, Boolean, Collection (JSON). Arrays unsupported (empty/not-empty filters only)
- **Semantic type** adds meaning, doesn't cast; Entity key, Foreign key (required for linked dashboard filters), Category, Email, URL, Currency, etc.
- Drives auto chart selection, drill-through, field filters, X-rays, map types

**Formatting** — global (Settings > Localization) < field (Table Metadata) < question visualization. Docs: `data-modeling/formatting`

**JSON unfolding** — Docs: `data-modeling/json-unfolding`

- Databases: BigQuery (STRUCT only, not JSON type), Druid, MongoDB, MySQL, PostgreSQL
- Toggle: Admin > Databases > advanced, or per-field Unfold JSON
- Unfolds nested objects, **not arrays**; column must be JSON data type in DB
- Query builder can't parse raw JSON — only Is empty / Is not empty without unfolding

**Editable tables** (**Pro/Enterprise**): Postgres/MySQL; Admin > Databases toggle; admin-only spreadsheet-style edits. Docs: `data-modeling/editable-tables`

---

## Data Studio

Access: **Admin** or **Data Analysts** group only (**Pro/Enterprise** for Data Analysts). Docs: `data-studio/overview`

| Feature | Plan | Docs path |
|---------|------|-----------|
| Library, Schema viewer, Dependency graph, Replace data sources | Pro/Enterprise | `data-studio/library`, `schema-viewer`, `dependencies/graph` |
| Transforms (basic query) | Self-hosted all; Cloud needs add-on | `data-studio/transforms/transforms-overview` |
| Python transforms, Transform inspector | Pro/Enterprise + Advanced add-on | `transforms/python-transforms`, `transform-inspector` |
| Workspaces | Pro/Enterprise | `data-studio/workspaces` |

### Library

Special collection: **Data** (published tables), **Metrics**, **Snippets**. Docs: `data-studio/library`

- Only admins/data analysts can **publish** tables (Curate on Library > Data does **not** grant publish to others)
- Published tables can't depend on non-Library tables (Metabase auto-publishes dependencies)
- **Collection permissions on Library > Data control UI visibility only — use data permissions for actual table access**
- Publishing a table grants query access to groups with database View even if Create Queries = No for that table
- Metrics in Library prioritized in query builder; Curate on Library > Metrics lets non-analysts save metrics from main app
- Remote sync for Library versioning (**Pro/Enterprise**)

### Managing tables

Docs: `data-studio/managing-tables`

- Data Analysts see metadata for **all** tables regardless of View Data permissions
- **Visibility layer**: Hidden (not in QB, not synced), Internal, Final — UX only, not access control
- Attributes: owner, entity type, source (auto: transforms, CSV uploads)
- Bulk publish, replace data sources

### Segments & measures (Data Studio)

Same semantics as above; create/edit requires Data Studio access + Create queries on table. Remote sync: only on published Library tables with Library sync enabled.

### Transforms

Docs: `data-studio/transforms/transforms-overview`, `query-transforms`, `jobs-and-runs`

- Query (SQL/QB) or Python → persistent table in target schema; replaces table each run (or incremental)
- Databases: BigQuery, ClickHouse Cloud, MySQL/MariaDB, Postgres, Redshift, Snowflake, SQL Server
- **Not** on: database routing DBs, Sample Database
- Requires writable DB user; use writable connection for isolation
- **OSS/Starter**: admins only see/run transforms. **Pro/Enterprise**: Data Analysts + per-database transform permissions (requires View + QB+native on all tables in DB)
- Tags + Jobs for scheduling; jobs include dependent transforms (skip if already fresh)
- Incremental: checkpoint column (monotonic), optional merge key for upsert
- SQL variables must have defaults or `[[optional]]` blocks
- Change target table: questions on old target **not** auto-transferred
- Remote sync YAML (**Pro/Enterprise**); read-only sync mode blocks create/edit

### Dependency graph

Docs: `data-studio/dependencies/graph`

- Tracks questions, models, snippets, transforms, metrics, dashboards, documents → tables
- Inferred dependencies (SQL refs, filter dropdown questions); replace data sources in bulk (**Pro/Enterprise**)

### Workspaces

Docs: `data-studio/workspaces`

- Isolated schema remapping for AI/agent experimentation; requires admin DB connection, remote sync
- Prod transforms write to real schema; workspace writes to isolated schema transparently

---

## Agent gotchas

1. **Hidden ≠ secure** — always set data permissions for real access control
2. **Metrics vs measures**: metrics = collection objects with dimensions; measures = table-scoped in Data Studio
3. **Segments/measures/metrics** only work when table is **primary** data source
4. **Model persistence** conflicts with sandboxing/impersonation
5. **Library Curate ≠ publish** — only Admin/Data Analysts publish tables
6. **Transforms successor to models** — recommend transforms for persisted derived tables
7. Data Analyst group gets Manage table metadata on **all** tables by default
