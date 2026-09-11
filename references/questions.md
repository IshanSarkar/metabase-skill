# Metabase Questions Reference

Official docs: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## What is a Question?

A **Question** = query + results + visualization. Basic analytical unit; saved to collections or dashboards. Docs: `questions/introduction`

Create via **+ New**:
- **Question** → graphical query builder (`questions/query-builder/editor`)
- **SQL/Native query** → SQL editor (`questions/native-editor/writing-sql`)
- **Metabot** (AI): natural language → chart/query

**Saving**: to dashboard (single-dashboard visibility) or collection (reusable across dashboards; needs Curate access). **Breaking change detection** on save (**Pro/Enterprise**): warns if column removals break downstream questions/models.

**Other**: bookmark, verify content, per-question caching (**Pro/Enterprise**), convert collection question → model, version history (15 versions). Docs: `exploration-and-organization/history`.

---

## Query builder

Docs: `questions/query-builder/editor`

Steps (notebook UI): **Pick data** → **Join** → **Custom columns** → **Filter** → **Summarize** → **Sort** → **Row limit** → **Visualize**.

- **Data sources**: table, model, metric, saved question. Library mode shows Data + Metrics only; "Browse all" for rest
- **Column pick**: unchecking excludes from results (not security — use permissions). Hiding in table viz ≠ excluding from query
- **Preview**: play button shows first 10 rows at any step
- **View SQL/Convert to SQL**: one-way conversion to native editor; requires query builder + native permissions
- **Row limits**: max display 2,000 (unaggregated) / 10,000 (aggregated) in table viz; `MB_AGGREGATED_QUERY_ROW_LIMIT` env var

### Filters

Docs: `questions/query-builder/filters`

Types by column: numeric (range, =, >, <), text/category (is, contains, starts/ends with, empty), date (specific vs relative ranges with optional offset), lat/long ("Inside"), JSON (empty/not empty only; use JSON unfolding). Post-summarize filters = SQL `HAVING`. **Segments** (admin-defined, purple in dropdown). Custom expression filters: `[Subtotal] > 100 OR median([Age]) < 40`.

### Summarize & group

Docs: `questions/query-builder/summarizing-and-grouping`

Built-in metrics: Count, Sum, Average, Distinct values, Cumulative sum/count, Std dev, Min, Max. Multiple summarize steps allowed. Group by datetime (day/week/month/quarter/year), numeric bins, lat/long bins. Admin **Metrics** and **Measures** appear in dropdown.

### Joins

Docs: `questions/query-builder/join`

Same database only. Types: left outer (default), right outer, inner, full outer. Auto-picks FK columns. Multi-stage joins (A→B→C). Multiple conditions (AND). Custom expression join keys (e.g., `concat([first_name]," ",[last_name])` = `[full_name]`, or `1=1` for cross join averages).

### Custom expressions

Docs: `questions/query-builder/expressions`, `questions/query-builder/expressions-list`

Spreadsheet-like formulas for custom columns, filters, summaries. Columns: `[Column]` or `[Table.Column]`. Segments/metrics: `[Segment Name]`.

**Aggregations** (Summarize only): `Count()`, `Sum()`, `Average()`, `Min()`, `Max()`, `Median()`, `Distinct()`, `CountIf(cond)`, `SumIf(col, cond)`, `DistinctIf(col, cond)`, `Share(cond)`, `StandardDeviation()`, `Variance()`, `Percentile(col, p)`, `CumulativeSum(col)`, `CumulativeCount()`, `Offset(expr, n)` (window; not MySQL/MariaDB/ClickHouse/MongoDB/Druid).

**Key functions**:
- Logic: `case`/`if`, `coalesce`, `between`, `in`, `notIn`, `isNull`, `notNull`, `isEmpty`, `notEmpty`
- Math: `abs`, `ceil`, `floor`, `round`, `sqrt`, `power`, `log`, `exp`
- String: `concat`, `contains`, `startsWith`, `endsWith`, `substring`, `replace`, `splitPart`, `regexExtract`, `lower`, `upper`, `trim`, `length`, `domain`, `host`, `path`
- Date: `now`, `today`, `datetimeAdd/Subtract/Diff`, `convertTimezone`, `relativeDateTime`, `year/month/day/hour/minute/second`, `week(mode)`, `weekday`
- Cast: `date`, `datetime`, `integer`, `float`, `text`

Operators: `+ - * /`, comparisons, `AND OR NOT`. Dates in filters: `"YYYY-MM-DD"`. Function browser: click **f** in editor.

**DB limitations** (summary): Median/Percentile missing on MariaDB, MySQL, MongoDB, SQL Server, SQLite, Vertica, Druid; Offset missing on MySQL/MariaDB/ClickHouse/MongoDB/Druid; regexExtract missing on MongoDB/SQLite/SQL Server. Full list: `expressions-list`.

---

## Native / SQL editor

Docs: `questions/native-editor/writing-sql`

Runs SQL exactly as written against selected database. Save, download, add to dashboards, convert to model. **Explore results** button (saved SQL without parameters): creates query-builder question from SQL results.

**Not supported**: multi-statement queries, stored procedures, DDL (`CREATE`/`ALTER`/`DROP`). With **impersonation**: enforced — single `SELECT` only.

**PostgreSQL**: use `??` instead of `?` JSON operator (JDBC conflict). **SQL formatter**: unavailable for SQLite and SQL Server. Run: Ctrl+Enter / ⌘+Return; run selection by highlighting.

**Drill-through limited** vs query builder: filter by click, zoom time series/maps, column header actions; no drill to unaggregated records, time granularity change, or category/location breakout.

---

## SQL parameters

Docs: `questions/native-editor/sql-parameters`

Variables create filter widgets; mappable to dashboard filters. Sidebar: **Variables and parameters**.

### Variable types

| Type | Syntax | Use |
|------|--------|-----|
| **Field filter** (preferred) | `WHERE {{var}}` (no column/operator) | Smart widgets: dropdowns, date ranges. Map to DB field in sidebar. Aliased tables: set **Table and field alias** (e.g., `p.category`) |
| **Basic** | `WHERE col = {{var}}` | Text, Number, Date, Boolean plain inputs. Multi-value: `IN ({{vars}})` |
| **Time grouping** | — | Change date grouping (month/week/day) |
| **Table** | — | Select which table to query |

Field filters handle multi-select and date ranges automatically. Basic variables lack dynamic date pickers.

### Optional clauses

Docs: `questions/native-editor/optional-variables`

Wrap entire clause: `[[WHERE category = {{cat}}]]`. Entire `WHERE` must be inside brackets. Multiple optionals: `WHERE TRUE [[AND id = {{id}}]] [[AND {{category}}]]`. Default values via comment trick: `[[ {{param}} --]] default_value`.

### Snippets

Docs: `questions/native-editor/snippets`

Reusable SQL blocks: `{{snippet: name}}`. Create by highlighting code > Save as snippet. Can contain parameters, nested snippets (no circular refs), saved question refs. Unique names (including archived).

### Referencing saved questions / models

Docs: `questions/native-editor/referencing-saved-questions-in-queries`

Syntax: `{{#123-name}}` or typeahead `{{#search term}}`. Works as subquery or CTE: `WITH x AS {{#5-question}} SELECT ...`. Same database required. SQL databases only. **Cannot reference variables** in sub-questions — only results.

URL params: `?variable_name=value` (multiple: `&`-separated).

---

## Visualizations

Docs: `questions/visualizations/visualizing-results`

Query builder auto-selects chart; native requires manual pick. Change via **Visualization** button bottom-left; gear for per-chart settings.

| Chart | When to use | Docs |
|-------|-------------|------|
| **Table** | Raw/tabular data, lists | `visualizations/table` |
| **Number** | Single big metric | `visualizations/numbers` |
| **Trend** | Single metric change between two periods | `visualizations/trend` |
| **Progress** | Single number vs goal | `visualizations/progress-bar` |
| **Gauge** | Single number in colored ranges | `visualizations/gauge` |
| **Line** | Metric over time (many x values) | `visualizations/line-bar-and-area-charts` |
| **Bar / Row** | Metric by category; row = many categories | `visualizations/line-bar-and-area-charts` |
| **Area** | Compare proportions over time (stackable) | `visualizations/line-bar-and-area-charts` |
| **Combo** | Bars + lines/areas combined | `visualizations/line-bar-and-area-charts` |
| **Histogram** | Count by numeric bin (auto when x = number) | `visualizations/line-bar-and-area-charts` |
| **Pie/Donut/Sunburst** | Proportions, small breakout count | `visualizations/pie-or-donut-chart` |
| **Scatter/Bubble** | Correlation between two variables | `visualizations/scatterplot-or-bubble-chart` |
| **Waterfall** | Positive + negative contributions | `visualizations/waterfall-chart` |
| **Funnel** | Step-wise conversion/flow | `visualizations/funnel` |
| **Map** | Auto-picks pin/grid/region from geo data | `visualizations/map` |
| **Pivot table** | Multi-dimension grouping with subtotals; **not available for native SQL** | `visualizations/pivot-table` |
| **Treemap** | Hierarchical data as nested rectangles | `visualizations/treemap` |
| **Sankey** | Multi-step flow volumes | `visualizations/sankey` |
| **Box plot** | Distribution (median, quartiles, outliers) | `visualizations/box-plot` |
| **Detail** | Single record two-column view | `visualizations/detail` |
| **Custom** | **Pro/Enterprise** — SDK-built chart types | `visualizations/custom` |

Formatting: per-column in viz settings; global defaults in `data-modeling/formatting`.

---

## Drill-through

Docs: `questions/visualizations/drill-through`

Click chart/table → menu → new question (doesn't modify original). Requires query-building permissions.

**Two types**:
- **Results-based** (query builder + SQL): Filter by value, Distribution, Sort
- **Query-rewriting** (query builder only): See these records, Break out by time/location/category, Zoom in

Table column headers: filter, sort, distribution, sum/avg, distinct values, extract domain/date parts, combine columns. Cells: filter, view details (PK), FK navigation, break out aggregated values. Charts: filter, zoom (time series), break out legend items. Pivoted tables behave like charts.

Save exploration as new question. Docs: `questions/visualizations/drill-through`.

---

## Alerts

Docs: `questions/alerts`

Questions only (not dashboards — use subscriptions). Requires email, Slack, or webhooks configured. Webhooks: admins + settings access only.

**Types**:
1. **Results alert**: any result returned (good for "bad review appeared" queries filtered to recent + rare)
2. **Goal line alert**: line/bar/area time series with goal line (above/below; every time or first time)
3. **Progress bar alert**: single number vs goal

Schedule: minute/hourly/daily/weekly/monthly/custom Quartz cron. Destinations: email, Slack, webhook. **Send once** option auto-deletes alert after firing. Test with **Send now** (question must return results).

---

## Exporting

Docs: `questions/exporting-results`

**Question**: Download button → .csv, .xlsx, .json, .png (charts). Formatted vs unformatted (raw). Pivot tables: export pivoted or unpivoted (flat Excel table, not native Excel PivotTable).

**Limits**: default 1,048,575 rows (`MB_DOWNLOAD_ROW_LIMIT` for CSV); XLSX capped at Excel max; 32,767 chars/cell.

**Dashboard**: PDF (Share > Export as PDF; tab-level on multi-tab), per-card download (.csv/.xlsx/.json/.png), subscriptions with attachments. Alt/Option+click for unformatted.

**Other**: public export links (`embedding/public-links`), alert attachments. **Remove Metabase branding** on exports: **Pro/Enterprise**.

Permissions: `permissions/data` download results setting.

---

## Metrics Explorer

Docs: `questions/metrics-explorer`

Ad-hoc analysis of **Metrics** (`data-modeling/metrics`) and **Measures** (`data-studio/measures`). **Not saveable** — share via URL (`/explore#...` encodes state). Use query builder for saved explorations.

**Open**: metric home page → Explore; or Data Studio > Tables > Measures → ⋮ → Explore.

**Features**:
- Plot metric/measure along best-fit dimension; change via **Break out** sidebar
- **Compare** multiple metrics/measures in search bar
- **Time/Country buckets**: collapse all date or country-semantic columns; slider to pick specific column per metric
- **Shared dimensions**: exact column match required (except Time/Country); FK-linked sources share dims
- **Series breakout**: per-metric additional dimension
- **Per-metric filters**
- **Math**: `+`, `-`, `*`, `/`, parentheses on metrics (e.g., `Revenue / Active users`) — especially useful cross-table without joins
- Zoom into time periods; toggle column labels

Compare metrics from different tables without manual joins when metrics explorer handles dimension matching.
