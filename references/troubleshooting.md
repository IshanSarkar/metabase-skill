# Metabase Troubleshooting Reference

Index: https://www.metabase.com/docs/latest/troubleshooting-guide/index

## Diagnostic workflow (start here)

### Download diagnostic info

- **Shortcut:** Cmd+F1 (Mac) / Ctrl+F1 (PC), or Cmd/Ctrl+K → "Open diagnostic error modal"
- **Includes (selectable):** item definition, browser errors, server errors/logs, instance version
- **Review before sharing** — may contain sensitive data
- **Admin path:** Admin > Tools > Logs; Diagnostic Info in Tools tab shows `application-database` key

**Server logs:** Admin > Tools > Logs, or `docker logs -f CONTAINER`. Look for sync, connection, SAML, Liquibase errors.

**HAR:** DevTools → Network → Export HAR (performance issues). **Profiling:** see profiling-metabase guide.

Docs: diagnostic-info, server-logs, create-har-file, profiling-metabase under troubleshooting-guide.

---

## Database connections

**Symptoms:** Can't connect, tables missing, sync stuck, "Connections cannot be acquired from the underlying database."

**Checklist:**
1. Admin > Databases → verify connection exists, click **Sync database schema**
2. Admin > Tools > Logs → sync/connection errors
3. Verify DB server running; test connection from Metabase host machine
4. Check IP whitelisting (Metabase Cloud: whitelist Metabase Cloud IPs)
5. Verify DB user has required privileges (SELECT on schemas/tables)
6. Metabase version must support DB version (e.g., Metabase <46 lacks SQL Server 2022 support)

**Common fixes:**
- SQL Server: add `trustServerCertificate=true` in JDBC connection string options
- BigQuery + Google Drive: see dedicated guide
- Connection succeeds but no tables → https://www.metabase.com/docs/latest/troubleshooting-guide/cant-see-tables

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/db-connection

---

## Sync, scan, fingerprinting

**Symptoms:** Missing tables/columns, wrong data types, stale filter dropdown values, data mismatch with DB.

**First:** Clear browser cache → refresh → try incognito.

**Sync issues:**
1. Update Metabase + community drivers
2. Check Admin > Tools > Logs for sync status
3. Test with SQL editor: `SELECT * FROM "schema"."table" LIMIT 1`
4. Manual re-sync: Admin > Databases > (db) > Sync database schema
5. New DB: initial sync takes time; if never starts → check connection

**Scan/fingerprinting:** filter dropdown values. **Slow JSON sync:** disable JSON unfolding (Admin > Databases > Advanced). **Force via API:** sync/scan endpoints at `/api/docs`.

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/sync-fingerprint-scan

---

## Permissions

**Symptoms:** Wrong access level, can't view/edit dashboards, can't see data/schemas/rows/columns, SQL editor blocked.

**Key principle:** Permissions are **additive** — most permissive group wins. Check if user is in multiple groups.

**Triage:**
1. Admin > People → check group memberships
2. Can't view/edit content → collection permissions
3. Can't access data → data permissions (schema/table/row/column/SQL)

**Common:** collection vs data permission mismatch; SQL blocked (no native query perm); RLS not applying to SQL; "permission denied" (wrong table/schema access).

Docs: permissions, data-permissions, row-and-column-security guides.

---

## SQL questions

**Symptoms:** Wrong aggregations, duplicated/missing rows, filter widgets broken, syntax errors.

**Common causes:**
- Field filters must connect to DB fields included in query (missing FROM clause error)
- Table aliases in SQL break field filters
- Filter widget not showing dropdown → change search box to dropdown in metadata
- JSON `?` operator fails on PostgreSQL → use `??`
- Wrong dates → timezone issues (see timezones guide)
- Stale data → sync/scan issue

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/sql, https://www.metabase.com/docs/latest/troubleshooting-guide/error-message

---

## Filters

**Symptoms:** No results, wrong results, filter widget empty.

**First:** Clear cache → refresh → incognito.

**Dashboard filters:**
1. Edit mode → gear icon on filter → verify **Column to filter on** set
2. If column missing or "No Results" → check underlying question

**Question filters:** column included, contains values, visible in metadata, user has data perms. Check custom column expressions and SQL field filter syntax. **Type mismatches:** cast column to match filter type. **Linked filters:** parent limits child dropdown.

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/filters, https://www.metabase.com/docs/latest/troubleshooting-guide/linked-filters

---

## Email and notifications

**Symptoms:** Alerts/subscriptions not arriving.

**Steps:** Admin > Email → verify settings → Send test email → check Logs for SMTP errors → verify delivery service from-address/domain → check spam/DKIM → test creds in another client.

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/cant-send-email, https://www.metabase.com/docs/latest/troubleshooting-guide/notifications

---

## Login and SSO

### General login

- Verify **Site URL** (Admin > Settings > General) matches actual URL
- Check account not deactivated (Admin > People)
- Reset password: admin can reset user password; admin password reset via token/email
- Metabase Cloud store password ≠ instance password

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/cant-log-in

### SAML (Pro/Enterprise)

| Error | Fix |
|-------|-----|
| Incorrect response `<issuer>` | Copy issuer/Entity ID from IdP metadata XML → Admin > Authentication > SAML |
| Invalid assertion | Verify certificate matches IdP metadata (include BEGIN/END lines) |
| SSO URL wrong | Must end with `/auth/sso` |
| Private key null | Keystore cert needs private key (Signed SSO requests) |

Check logs: Admin > Tools > Logs. Login page should show single IdP button when working.

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/saml, https://www.metabase.com/docs/latest/troubleshooting-guide/ldap

### Embedding auth issues

- Cross-domain SSO: SameSite=None + HTTPS; Safari needs cross-site tracking enabled
- JWT SSO for SDK: endpoint must return `{ jwt: "..." }` for `?response=json` requests
- Guest embed: verify secret key matches; all locked params in JWT; token not expired

---

## Timeouts

**Symptoms:** "Your question took too long", queries hanging.

**Sources:** DB connection, load balancer, reverse proxy (Nginx), Jetty, cloud platform.

**Actions:**
- Check DB connection health and query performance
- Increase proxy/load balancer idle timeout
- Review Jetty connector settings
- See db-performance guide for slow queries

Docs: https://www.metabase.com/docs/latest/troubleshooting-guide/timeout, https://www.metabase.com/docs/latest/troubleshooting-guide/db-performance, https://www.metabase.com/docs/latest/troubleshooting-guide/my-dashboard-is-slow

---

## H2 application database

**Default dev DB — not for production.** Sensitive to filesystem corruption.

**Check current app DB:** Admin > Tools > Diagnostic Info → `application-database` key.

**Migrate to Postgres/MySQL:** use `load-from-h2` command (see migrating-from-h2 docs).

**Common migration errors:**
- File must be named `metabase.db.mv.db`
- Path on command line must NOT include `.mv.db` extension (H2 adds it)
- Example: `java -jar metabase.jar load-from-h2 /path/to/metabase.db`

**Liquibase lock:** `Could not acquire change log lock` → previous run didn't clean up; see loading-from-h2 guide for unlock steps.

**Downgrade:** not supported (restore backup + older JAR). Docs: loading-from-h2, migrating-from-h2.

---

## Docker

**Diagnostic sequence:**
1. `docker ps` — container running?
2. `docker logs CONTAINER` — server started? Look for "Metabase Initialization COMPLETE"
3. App database configured correctly (env vars `MB_DB_*`)?
4. Port accessible from host?
5. Shell into container: `docker exec -ti CONTAINER bash`

**Common:** container exits (app DB errors in logs); shutdown after init (DB config); data loss (missing volume/`MB_DB_*`); wrong port mapping. Docs: docker guide.

## Other issues & escalation

Also see: proxies (can't save), cant-view-or-edit, visualization, timezones, models, known-issues, bugs guides.

**Escalate with:** diagnostic info + HAR, server logs, Metabase version. Search discourse.metabase.com; check GitHub releases and upgrade. Cloud: https://www.metabase.com/help-premium
