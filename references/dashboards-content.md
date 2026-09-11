# Metabase Dashboards, Documents, Actions & Organization Reference

Official docs: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## Dashboards

Docs: `dashboards/introduction`, `filters`, `interactive`, `subscriptions`, `actions`

**Structure**: tabs, cards (questions, heading/text, link, iframe). Questions saved to collection vs dashboard-only (not reusable across dashboards).

### Filters & parameters

Docs: `dashboards/filters`

**Filter widgets** (what data): Date picker, Location, ID, Number, Text/Category, Boolean  
**Parameter widgets** (how displayed): Time grouping (doesn't filter — changes aggregation granularity)

**Placement**: dashboard-level (all tabs), header-level (tab), card-level (single card). Prefer dashboard-level.

**Native/SQL cards**: need field filters or basic variables; basic variables limit to single-value filter types. Time grouping in SQL needs time grouping parameters.

**Configuration**: rename, change type (disconnects cards), operator, input type (dropdown/search/input), multi-select, selectable values (connected field / another model / custom list), default, required (needs default), auto-apply toggle (off = Apply button).

**Linked filters** (`dashboards/linked-filters`): child filter values restricted by parent; requires FK relationships in **table metadata** (not model/question joins). Child = ID/Location/Text; native needs field filters. No custom columns, custom lists, or "from another question" sources.

**Cross-filtering** (`dashboards/interactive`): navigation question updates dashboard filter; wire other cards to filter, leave navigation card disconnected.

### Interactive click behavior

Docs: `dashboards/interactive`

- QB questions: drill-through menu (default), custom destination (dashboard/question/URL), update dashboard filter
- SQL questions: custom destination + update filter only
- Pass column values or dashboard filter values to destination filters; per-column click behavior on tables
- **Pro/Enterprise**: pass SSO user attributes to destination filters

### Dashboard features

- Sections (KPI templates), duplicate tab, fixed/full width, auto-refresh, fullscreen, URL params (`#refresh=60&fullscreen`)
- Card viz settings on dashboard override question settings (dashboard-only)
- Hide card if no results (query still runs)
- Duplicate dashboard: copies layout/filters/questions; **not** subscriptions, actions, public/embedding settings
- Version history: last 15 versions (`exploration-and-organization/history`)
- **Pro/Enterprise**: dashboard caching, verification (sticky — layout changes keep badge)

### Subscriptions

Docs: `dashboards/subscriptions`

- Email or Slack; can send to non-Metabase users
- Frequencies: hourly, daily, weekly, monthly; test with "Send now"
- Attachments: CSV/XLSX (up to ~1M rows default), unformatted option, PDF of dashboard
- Skip if no results; custom viz falls back to default (no user session)
- **Pro/Enterprise**: per-subscription filter values (different views per recipient group)
- **Pro/Enterprise**: approved email domains, suggest recipients
- Embedded dashboard subscriptions omit Metabase links
- Permissions: `permissions/notifications` — recipients see **creator's** data/collection permissions

### Actions on dashboards

Docs: `dashboards/actions`, `actions/introduction`

- Requires model with actions (Postgres/MySQL; Model actions enabled on DB + write perms)
- Button connects to action; fields from user input or dashboard filter
- **Not** on public dashboards or guest embeds; use public action forms or modular/full-app embedding

---

## Actions

Docs: `actions/introduction`, `basic`, `custom`

- Parameterized SQL writing to **underlying table** (not model definition)
- Create/edit: Native query editing on database; Run: view access to model/dashboard/public form
- Basic actions: single raw table models only; Custom: any SQL
- No undo; caching may delay visibility; Postgres/MySQL only
- vs editable tables: admin spreadsheet edits vs custom forms for non-admins

---

## Documents

Docs: `documents/introduction`

- Markdown narrative + charts (questions/models); `/` commands, `@` mentions
- Chart from collection = **copy** (independent); chart created in doc = lives in doc only (permanent delete, not in trash)
- Layout: up to 3 items side-by-side; supporting text per chart group
- Comments on sections/charts; email on mentions
- Public links (**admin** enables)
- Use for stories/exploration; dashboards for monitoring/filtering

---

## Collections & organization

Docs: `exploration-and-organization/collections`

**Types**: Regular, **Official** (**Pro/Enterprise** — yellow badge, search boost), **Library** (**Pro/Enterprise**), personal (fixed permissions), Our analytics (immortal), Usage analytics

**Permission levels**: Curate (edit/move/delete/pin/events), View, No access

**Gotcha — additive/most permissive**: person in multiple groups gets **most permissive** collection access. **All Users with Curate overrides restrictive groups.** Block All Users before restricting.

**Sub-collections**: changing parent doesn't retroactively change existing sub-collections unless "Also change sub-collections" toggled; new sub-collections inherit parent.

**Dashboard multi-collection**: viewer needs View on all source collections or sees permission error on cards.

**Pinned items**: Curate required; visible to all viewers of collection.

**Cleanup** (**Pro/Enterprise**): bulk trash unused items by age.

### Trash

Docs: `exploration-and-organization/delete-and-restore`

- Questions, dashboards, models, metrics, collections (not permanently deletable)
- Visible in Trash only with Curate on source collection
- Delete question → removes dashboard cards; alerts removed (not restored); dependent questions break if permanent delete
- Delete dashboard → dashboard-only questions trashed; subscriptions deactivated
- Segments: retire (permanent, not in trash); snippets: archive; events/timelines: archive (not in trash)

### X-rays

Docs: `exploration-and-organization/x-rays`

- Auto insights from charts, tables, models; save as dashboard to "Automatically generated dashboards"
- Admin can disable: Settings > General > Enable X-ray features

### Content verification

Docs: `exploration-and-organization/content-verification` (**Pro/Enterprise**)

- Admin verifies questions, models, metrics, dashboards
- Query change on question/model/metric removes verification; dashboard verification persists through edits

### Events & timelines

Docs: `exploration-and-organization/events-and-timelines`

- Events on time series **individual questions only** (not dashboard cards)
- Timelines per collection (not sub-collections, not Library)
- Curate to add/edit; View to see; put in All Users-accessible collection for org-wide timelines

---

## Agent decision guide

| Need | Use |
|------|-----|
| Daily KPI monitoring, cross-chart filters | Dashboard |
| Narrative + comments | Document |
| Write-back workflows | Actions (+ dashboard buttons) |
| Official curated tables/metrics | Library (Data Studio) |
| One-off exploration | Question in collection or personal collection |
| Institutional calendar context | Events/timelines on collection |

**Critical permissions interactions**:
- Collection Curate without data access ≠ can edit queries
- Blocked data permission overrides collection access to questions on that data
- Dashboard subscription recipients inherit **creator's** permissions, not their own
- Public links bypass row/column security — disable public sharing if sandboxed
