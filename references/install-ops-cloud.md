# Metabase Install, Ops & Cloud Reference

Metabase ships as a Java JAR (OSS or Enterprise/Pro) or official Docker/Podman images; default port 3000 via embedded Jetty.
Production requires an external application database (Postgres recommended); H2 is demo-only and data is lost if the container is removed.
Configure via Admin UI, environment variables (highest precedence), or Pro/Enterprise `config.yml` on startup (self-hosted only).
Metabase Cloud manages infra, upgrades, backups, SMTP, SSL; self-host gives full control but you own ops, HA, and backups.
Pro/Enterprise unlock serialization, remote sync, config file, usage analytics, custom appearance, advanced caching, dev instances.

Docs URL pattern: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## Install Methods

| Method | Image/JAR | Notes |
|--------|-----------|-------|
| **Cloud** | Managed | Auto upgrades/backups/SSL/SMTP. `cloud/start` |
| **Docker** | `metabase/metabase`, `metabase/metabase-enterprise` | Mount `/plugins` for JDBC drivers. `MUID`/`MGID` for file perms. `installation-and-operation/running-metabase-on-docker` |
| **JAR** | OSS or enterprise JAR | Java 25 (Temurin). `java --add-opens java.base/java.nio=ALL-UNNAMED -jar metabase.jar`. `installation-and-operation/running-the-metabase-jar-file` |
| **Podman** | Same Docker Hub images | `installation-and-operation/running-metabase-on-podman` |
| **systemd** | JAR + `.env` | Unprivileged user; bind `127.0.0.1:3000`, Nginx proxy. `installation-and-operation/running-metabase-as-service` |
| **Azure Web App** | Docker | VNET + private Postgres, min ~200 ACU / 3.5GB RAM. Health: `/api/health`. `installation-and-operation/running-metabase-on-azure` |

No official Helm chart or AWS/Azure Marketplace. Elastic Beanstalk guide exists.

---

## Java & Runtime

Java 25 required; always use `--add-opens java.base/java.nio=ALL-UNNAMED`. Set `JAVA_TIMEZONE` or `-Duser.timezone` to match report timezone. Health: `GET /api/health`.

---

## Application Database

Stores Metabase metadata—not your warehouse. **Cannot change while running.** Check: `GET /api/bug-reporting/details` → `application-database`.

| Engine | Production? | Min version |
|--------|-------------|-------------|
| **PostgreSQL** | ✅ Recommended | 14+ |
| **MySQL/MariaDB** | ✅ | MySQL 8.4+ / MariaDB 10.6+ (`utf8mb4`) |
| **H2** | ❌ Demo | File: `metabase.db.mv.db` |

Env: `MB_DB_TYPE`, `MB_DB_HOST`, `MB_DB_PORT`, `MB_DB_DBNAME`, `MB_DB_USER`, `MB_DB_PASS`, or `MB_DB_CONNECTION_URI`. IAM: `MB_DB_AWS_IAM`, `MB_DB_AZURE_MANAGED_IDENTITY_CLIENT_ID`. Docs: `installation-and-operation/configuring-application-database`.

### H2 → Postgres/MySQL

Stop Metabase → backup H2 → **same version** throughout → `java ... -jar metabase.jar load-from-h2 /path/to/metabase.db` (omit `.mv.db`) → start with prod DB env. Target DB empty. Docker: extract H2, run JAR on host. Manual schema: `MB_DB_AUTOMIGRATE=false`. Docs: `installation-and-operation/migrating-from-h2`.

---

## Backups & Upgrades

Backup app DB only. H2: stop + copy `metabase.db.mv.db`. Docker H2: `docker cp metabase:/metabase.db/metabase.db.mv.db ./`. Postgres/MySQL: standard dump.

Self-host upgrade: backup → stop → pull specific tag → restart (same DB env). Cluster: **1 node** during major upgrade. Pre-v40: step through to v40 first. Downgrade: restore backup; or `migrate down` on higher-version JAR.

Cloud: auto-upgrades (minor ~1wk, major ~months). SDK Cloud instances pinned—email support. Docs: `installation-and-operation/upgrading-metabase`, `installation-and-operation/backing-up-metabase-application-data`.

---

## Serialization & Remote Sync (Pro/Enterprise)

**Serialization**: YAML export/import. CLI: `export <dir>`, `import <dir>`. Cloud: `POST /api/ee/serialization/export|import` (`.tgz`). Same major version. Not a backup. Excludes users, permissions, alerts, DB creds, license tokens. Flags: `-c`, `-C`, `-S`, `-D`, `-f`. Docs: `installation-and-operation/serialization`.

**Remote Sync**: Git push/pull from UI. Read-write (dev) / Read-only (prod, auto-sync 5min). Syncs collections, Library, snippets, transforms—not users, permissions, DB connections, table metadata. Self-contained collections; one branch per instance. Local: `file:///path/to/bare.git`. Docs: `installation-and-operation/remote-sync`.

---

## CLI & JAR Commands

**`mb` CLI**: Node 20.6+, Metabase 58+. `npm i -g @metabase/cli`; `mb auth login --url <url>`. `git-sync` needs Pro/Ent. Docs: `installation-and-operation/metabase-cli`.

**JAR** (`java ... -jar metabase.jar help`):

| Command | Purpose |
|---------|---------|
| `load-from-h2 <path>` | H2 → Postgres/MySQL |
| `export` / `import` | Serialization (Pro/Ent) |
| `migrate up\|down\|force\|print` | Schema migrations |
| `enable-encryption` / `rotate-encryption-key` | App DB encryption |
| `reset-password <email>` | Password reset |
| `config-template` | Generate config YAML |

Docs: `installation-and-operation/commands`.

---

## Environment Variables (Highlights)

Env vars override Admin UI; not stored in app DB. Cloud: contact support.

| Variable | Purpose |
|----------|---------|
| `MB_DB_*` | App database |
| `MB_JETTY_PORT` / `MB_JETTY_HOST` | HTTP (default 3000) |
| `MB_JETTY_SSL*` | Direct HTTPS |
| `MB_SITE_URL` | Public URL (emails, auth, embedding) |
| `MB_PREMIUM_EMBEDDING_TOKEN` | Pro/Ent license |
| `MB_CONFIG_FILE_PATH` | Config YAML path (Pro/Ent) |
| `MB_ENCRYPTION_SECRET_KEY` | Encrypt app DB secrets (min 16 chars) |
| `MB_PROMETHEUS_SERVER_PORT` | Prometheus scrape port |
| `MB_DB_AUTOMIGRATE` | `false` = manual migration SQL |
| `MB_DB_QUERY_TIMEOUT_MINUTES` | Query timeout (Cloud max 20 min) |
| `MB_AUDIT_MAX_RETENTION_DAYS` | Usage analytics retention (default 720) |
| `MB_EMAIL_SMTP_*` | SMTP; `*_OVERRIDE` for Cloud custom SMTP |

Docker secrets: `MB_DB_PASS_FILE`, etc. Full list: `configuring-metabase/environment-variables`.

---

## Config File (Pro/Ent, Self-Host)

`config.yml` in JAR dir or `MB_CONFIG_FILE_PATH`. Sections: `settings`, `users`, `databases`, `api-keys`. Kebab-case keys; `{{ env VAR }}` templates. **Overwrites Admin UI on restart.** New installs need `MB_PREMIUM_EMBEDDING_TOKEN`. Docs: `configuring-metabase/config-file`.

---

## Email, Slack, Webhooks

**Email**: SMTP for resets, invites, subscriptions, alerts. Cloud default SMTP cannot customize from-domain without **custom SMTP (Pro/Ent)**. Docs: `configuring-metabase/email`.
**Slack**: OAuth app for subscriptions/alerts. Docs: `configuring-metabase/slack`.
**Webhooks**: Alerts only (not subscriptions). JSON + base64 PNG. Docs: `configuring-metabase/webhooks`.

---

## Caching, Timezones, Localization, Appearance

**Caching**: question/dashboard/database policies. Duration/Schedule/Auto-refresh = Pro/Ent; Adaptive = all. `configuring-metabase/caching`.
**Timezones**: Align DB (UTC), JVM, report timezone. Cloud TZ: contact support. `configuring-metabase/timezones`.
**Localization**: language, formats. `configuring-metabase/localization`.
**Appearance** (Pro/Ent): colors, logo, white-label. `configuring-metabase/appearance`.

---

## Jetty

`MB_JETTY_PORT`, `MB_JETTY_HOST` (`0.0.0.0`), `MB_JETTY_SSL*` + keystore, `MB_JETTY_MAXTHREADS`, `MB_JETTY_SKIP_SNI` (default true). Prefer reverse proxy for SSL. `configuring-metabase/customizing-jetty-webserver`.

---

## Metabase Cloud

Managed HA, Postgres app DB, SMTP, SSL, backups, monitoring, SOC2. **Limits**: official drivers only (no SQLite/H2/community); no app DB access; 20-min query timeout; no from-address customization without custom SMTP. `cloud/limitations`.

**Self-host when**: HIPAA/custom regs, Metabase fork, community drivers, air-gap. `cloud/cloud-vs-self-hosting`.

**IPs to whitelist** (`cloud/ip-addresses-to-whitelist`): us-east-1 `18.207.81.126, 3.211.20.157, 50.17.234.169`; eu-central-1 `18.192.2.142, 18.184.191.58, 3.65.184.173`; ap-southeast-1 `54.179.42.215, 3.1.176.8, 18.139.48.211`; ap-southeast-2 `13.238.131.1, 3.105.237.132, 54.252.39.14`; sa-east-1 `18.228.120.123, 54.207.106.108, 18.228.120.162`.

**Custom domain** (Pro/Ent): Store → CNAME `us-1.cd.metabaseapp.com`. `cloud/custom-domain`.
**Storage** (add-on): CSV upload via ClickHouse; Google Sheets sync. `cloud/storage`.
**→ Cloud**: Admin > Cloud → snapshot → Store checkout. Update OAuth/SAML/embedding URLs. `cloud/migrate/guide`.
**Cloud → self-host**: Success team snapshot (`.mv.db`) → `load-from-h2`; match major version; new Pro token. `cloud/migrate/cloud-to-self-hosted`.
**Dev instances** (Pro/Ent add-on): flat-fee, watermarked, v55+, not prod. `installation-and-operation/development-instance`.

---

## Monitoring

**Prometheus**: `MB_PROMETHEUS_SERVER_PORT=9191`; scrape separate from app port. JVM, Jetty, c3p0, email metrics. `installation-and-operation/observability-with-prometheus`.
**JMX**: `-Dcom.sun.management.jmxremote*` port 1099; Docker via `JAVA_OPTS`. Trusted network only. `troubleshooting-guide/profiling-metabase`.
**Monitor UI**: dependency diagnostics, erroring questions, alerts (Pro/Ent), background tasks, logs, CLI analytics (Pro/Ent). `monitor/start`.

---

## Usage Analytics (Pro/Enterprise)

Read-only collection: activity/view/query logs, performance dashboards. Retention 720d (`MB_AUDIT_MAX_RETENTION_DAYS`). OSS/Starter: no Activity/View data. MySQL app DB: percentile cards broken—use Postgres. `usage-and-performance-tools/usage-analytics`. CLI analytics: `monitor/cli-analytics`.

---

## Plan Matrix (selected)

| Feature | OSS/Starter | Pro/Ent |
|---------|-------------|---------|
| Serialization / Remote Sync | ❌ | ✅ |
| Config file, Usage analytics | ❌ | ✅ |
| Custom appearance, adv. caching | ❌ | ✅ |
| Custom SMTP/domain on Cloud | ❌ | ✅ |
| Dev instances, Monitor Pro tabs | ❌ | ✅ |

---

## Common Gotchas

1. H2 in prod → corruption/data loss; migrate early.
2. Never migrate H2 and upgrade in same step; version must match.
3. Docker `MB_DB_HOST` must resolve inside container.
4. Azure Postgres: encode `@` as `%40` in URI.
5. Config file overwrites UI on restart; env vars immutable in UI.
6. Serialization ≠ backup; tokens excluded.
7. Cluster upgrade: single node during major migration.
8. Cloud: 20-min query timeout; no from-address without custom SMTP.
9. Encryption: set key → `enable-encryption` once (stopped).
10. Downgrade unsupported without backup/`migrate down`.

---

## Key Doc Paths

`installation-and-operation/installing-metabase` · `running-metabase-on-docker` · `running-the-metabase-jar-file` · `configuring-application-database` · `migrating-from-h2` · `backing-up-metabase-application-data` · `upgrading-metabase` · `serialization` · `remote-sync` · `commands` · `metabase-cli` · `observability-with-prometheus` · `configuring-metabase/environment-variables` · `config-file` · `email` · `caching` · `timezones` · `cloud/start` · `usage-and-performance-tools/usage-analytics`
