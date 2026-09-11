# Metabase Databases Reference

Official docs: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## Adding & managing databases

**Path**: Admin > Databases > Add a database. Per-driver fields differ. Docs: `databases/connecting`

**Official drivers** (Metabase team maintained; **Pro/Enterprise** get official support; oldest supported version through latest stable):

| Driver | Docs path |
|--------|-----------|
| Athena | `databases/connections/athena` |
| BigQuery | `databases/connections/bigquery` |
| ClickHouse | `databases/connections/clickhouse` |
| Databricks | `databases/connections/databricks` |
| Druid | `databases/connections/druid` |
| MongoDB | `databases/connections/mongodb` |
| MariaDB | `databases/connections/mariadb` (use **MySQL** driver) |
| MySQL | `databases/connections/mysql` |
| Oracle | `databases/connections/oracle` |
| PostgreSQL | `databases/connections/postgresql` |
| Presto | `databases/connections/presto` |
| Redshift | `databases/connections/redshift` |
| Snowflake | `databases/connections/snowflake` |
| SparkSQL | `databases/connections/sparksql` |
| SQL Server | `databases/connections/sql-server` |
| SQLite | `databases/connections/sqlite` |
| Starburst | `databases/connections/starburst` |
| Vertica | `databases/connections/vertica` |

Other engines: [community drivers](https://www.metabase.com/docs/latest/developers-guide/community-drivers). **H2 as data warehouse removed** (v46.6.4+); H2 still ships as embedded application DB only. Cloud provider notes: `databases/connections/aws-rds`.

**Multiple connections** to same database with different users/roles supported for privilege separation.

---

## Database privileges

Docs: `databases/users-roles-privileges`

**Minimum (read-only analytics)**: `CONNECT` + `SELECT` on schemas/tables used. Pattern: role `analytics` → user `metabase`.

**Optional write roles** (separate roles recommended; use [writable connection](#writable-connection) when possible):

| Feature | Privileges | Role name pattern |
|---------|-----------|-------------------|
| Actions / editable tables | `INSERT`, `UPDATE`, `DELETE` on target tables | `metabase_writer` |
| Model persistence | `CREATE` + write on persistence schema | `metabase_model_persistence` |
| Transforms | `CREATE TABLE`/`ALTER`/`DROP` on transform schema; may need `CREATE SCHEMA` (ClickHouse: `CREATE DATABASE`) | `metabase_transforms` |
| CSV uploads | `INSERT`, `UPDATE`, `DELETE` on upload schema | `metabase_uploads` |

Also optional: `TEMPORARY`, `EXECUTE` (stored procs). **Multi-tenant**: one DB connection per customer with scoped roles. Docs: `permissions/embedding`.

---

## Sync, scan, fingerprint

Docs: `databases/sync-scan`

| Operation | When | What it does |
|-----------|------|--------------|
| **Sync** | Hourly (default); cannot disable | Schema metadata: tables, views, columns, types, PKs, FKs; deactivates deleted tables. Fast `WHERE 1<>1 LIMIT 0` probe. |
| **Scan** | Daily (default) | Caches up to 1000 distinct values/column for filter dropdowns; max 100 kB text/column. Only **active fields** (used in last 14 days). |
| **Fingerprint** | Once at setup (optional periodic) | Samples first 10,000 rows: distinct count, null %, min/max, quartiles, semantic type hints (URL, email, geo). |

**Scan schedule options** (Admin > Databases > advanced): regularly / only when adding filter widget / never (manual). Dropdown fields set to "list of all values" scan on widget use if cache stale (>14 days).

**Manual**: Admin > Databases > Sync schema; Admin > Table Metadata > gear > Re-scan table/field; Discard cached values.

**Hide tables** (Table Metadata eye icon): excluded from query builder + data reference; still queryable via SQL.

**API**: `POST /api/database/{id}/sync_schema`, `/rescan_values`; `POST /api/notify/db/{id}` (requires `MB_API_KEY` env var). Docs: `api`.

**Periodic refingerprint**: increases DB load; improves UI suggestions (auto-binning).

---

## SSH tunneling

Docs: `databases/ssh-tunnel`

Use when direct connection blocked (bastion) or DB local-only (`Host=localhost`, tunnel to remote). Auth: username/password or SSH key (PKI). Bastion needs `AllowTcpForwarding yes`. **Metabase Cloud**: no VPN; use SSH tunnel. Whitelist [Cloud IPs](https://www.metabase.com/docs/latest/cloud/ip-addresses-to-whitelist). Slower than direct; connections drop on network change.

---

## SSL certificates

Docs: `databases/ssl-certificates`

Toggle "Use a secure connection (SSL)" + JDBC connection string options. Postgres example: `sslmode=verify-full&sslrootcert=/path/to/cert.pem`. Docker certs: `/app/certs/rds-combined-ca-bundle.pem`, `DigiCertGlobalRootG2.crt.pem`. **Metabase Cloud**: upload via Admin > Databases > SSL Client Certificate. Truststores (verify server) and keystores (mutual auth); RDS forbids keystores. App DB SSL via `MB_DB_CONNECTION_URI`.

---

## Connection encryption at rest

Docs: `databases/encrypting-details-at-rest`

Set `MB_ENCRYPTION_SECRET_KEY` (≥16 chars; `openssl rand -base64 32`). New DBs auto-encrypted. Existing: backup → stop → `java -jar metabase.jar enable-encryption` → restart. Rotate: `rotate-encryption-key new-key`. Disable: rotate to `""`. **Pro/Enterprise** self-hosted: also via config file. Losing key = reset all connection details.

---

## CSV uploads

Docs: `databases/uploads`, `exploration-and-organization/uploads`

**Supported DBs**: PostgreSQL, MySQL, Snowflake, Redshift, ClickHouse (**Cloud only**).

Setup: Admin > Settings > Uploads → select DB + schema (+ optional table prefix). Requires write-capable connection. Creates table + wrapping model in target collection. Permissions: View data + Create queries on upload schema; Curate on collection.

**MySQL speed tip**: set `local_infile=ON` on MySQL server (not Metabase); otherwise slow fallback.

---

## Writable connection

Docs: `databases/writable-connection`

**Requires Advanced transforms add-on.** Optional second connection for write ops while main stays read-only (can point to read replica vs primary). Used for: transforms, CSV uploads, editable tables, actions, model persistence. Same engine required; **incompatible with database routing**.

---

## Deleting databases & Sample Database

**Delete connection** (Admin > Databases > Danger Zone > Remove): **irreversible** — deletes all questions, models, metrics, segments based on that connection (not the actual warehouse data). Restore only from application DB backup. Docs: `databases/danger-zone`, `databases/connecting`.

**Sample Database** (H2, built-in demo data): if deleted, restore via Admin > Databases > **Bring the Sample Database back**. Docs: `databases/connecting`.

---

## Per-driver gotchas

### PostgreSQL
Docs: `databases/connections/postgresql`
- SSL modes: allow/prefer/require/verify-ca/verify-full; client cert must be PKCS8/DER
- Schema filter: All / Only these / All except (`*` wildcard)
- JSON unfolding on by default; toggle per column
- **Pro/Enterprise** self-hosted: Azure Managed Identity, OAuth, IAM (RDS) auth providers
- JDBC options: `options=-c%20key=value` (percent-encoded)

### MySQL
Docs: `databases/connections/mysql`
- Uses **MariaDB connector** — MySQL 8+ needs `mysql_native_password` for Metabase user
- Docker MySQL 8: `--default-authentication-plugin=mysql_native_password`
- Host mismatch (Docker): create user for actual connecting IP, not `localhost`
- JSON schema inferred from **first 500 rows** only
- Vitess/PlanetScale: add `LIMIT` in subqueries; metadata from information_schema may fail
- Non-UTF8 passwords: `passwordCharacterEncoding=` in JDBC options
- SSL fallback: `trustServerCertificate=true`

### MariaDB
Docs: `databases/connections/mariadb`
- Select **MySQL** driver. **No JSON unfolding**. JSON schema inference doesn't work.

### Snowflake
Docs: `databases/connections/snowflake`
- Account format: `{id}.{region}.aws` (region-dependent); or hostname from app.snowflake.com
- Auth: password or RSA key (+ passphrase). Requires warehouse; database name case-sensitive
- **Role field sets default only** — Metabase gets **all roles granted to user combined**; use connection impersonation for `SET ROLE` behavior
- No model features yet. Supports uploads.

### BigQuery
Docs: `databases/connections/bigquery`
- Service account JSON; roles: BigQuery Data Viewer, Metadata Viewer, **Job User** (not BigQuery User)
- Project ID without prefix; datasets = schemas (enter `marketing`, not `marketing.campaigns`)
- "Include User ID and query hash" disables BQ result caching (audit/debug)
- Native SQL defaults to **Standard SQL**; `#legacySQL` directive for Legacy SQL
- Google Drive via external BQ tables; share sheet with service account email
- Database routing works between projects with identical schemas. No model features.

### MongoDB
Docs: `databases/connections/mongodb`
- Connect via fields or connection string; cert only via fields (not string params `tlsCertificateKeyFile` etc.)
- Atlas: whitelist IPs; add DB name to connection string; may need **Use DNS SRV**
- Sync samples first+last 500 docs/collection; max 1000 leaf fields/collection
- Recommend `readPreference=secondary` for clusters
- New fields may not appear — workaround: include all keys in first doc with null values
- Sync slower than relational DBs

### Redshift
Docs: `databases/connections/redshift`
- User needs `information_schema` access for sync/scan
- Model persistence supported (not actions/editable tables). Supports uploads.

### ClickHouse
Docs: `databases/connections/clickhouse`
- Multiple databases space-separated; "Scan all databases" option
- JDBC server settings prefixed `clickhouse_setting_`
- Uploads: **ClickHouse Cloud only**. No model features.

### Databricks
Docs: `databases/connections/databricks`
- Host + HTTP path (SQL warehouse endpoint); PAT or OAuth M2M service principal
- **Default catalog required**; can't sync legacy `samples`/`hive_metastore`
- Multi-catalog toggle; routing: same-host catalogs when multi-catalog off, separate hosts when on
- No model features.

### SQL Server
Docs: `databases/connections/sql-server`
- Port empty = Dynamic Ports. Instance name for multi-instance hosts
- Azure SQL: port 1433
- SQL formatter unavailable for SQL Server

### Oracle
Docs: `databases/connections/oracle`
- **Requires manual JDBC driver**: download `ojdbc8.jar` → `plugins/` dir → restart
- Min driver + DB version: 19c. SID or service name
- Autonomous DB: download wallet, configure via `JAVA_OPTS` keystore; mutual TLS
- `date`/`datetime`/`float`/`splitPart` expression functions unavailable

---

## Common database settings

Most relational drivers share:
- **Re-run queries for simple explorations**: auto-run on Summarize/filter (disable if slow)
- **Choose when syncs and scans happen** + **Periodically refingerprint tables**
- **Database routing** (**Pro/Enterprise**): one question, different DB per viewer. Docs: `permissions/database-routing`
- **Model features**: actions, persistence, editable tables (where supported; need write perms)
