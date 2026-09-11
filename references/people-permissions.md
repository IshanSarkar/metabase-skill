# Metabase People, SSO & Permissions Reference

Official docs: `https://www.metabase.com/docs/latest/<path>` (omit `.md`).

---

## Accounts & groups

Docs: `people-and-groups/managing`

**Accounts**: email required; active on Create (counts toward billing on paid plans). Deactivate (not delete) preserves content. No true account deletion.

**Default groups** (cannot remove):
- **Administrators** — full admin + unrestricted data access
- **All Users** — every person always a member; use for **default/baseline** access only
- **Data Analysts** (**Pro/Enterprise**) — Data Studio, Library Curate, Manage table metadata on **all** tables (fixed)

**Group managers** (**Pro/Enterprise**): add/remove members, promote managers, rename group; not admins.

**User attributes** (**Pro/Enterprise**): key-value per person; manual or SSO sync. Required for row/column security; used for impersonation role mapping, database routing slugs, JWT/SAML/OIDC group sync.

**Special accounts** (not in People list): Anonymous (ID 0, public views), Internal Metabase (ID 13371338).

### Critical: most permissive group wins

Permissions granted to **groups**, not individuals. Person in multiple groups gets the **most permissive** access across **all** groups for both data and collections.

**All Users gotcha**: everyone is always in All Users. If All Users has Curate on a collection or Can view on data, **no other group restriction can reduce that access**. Metabase warns when All Users is more permissive than the group you're editing — **block All Users first**, then grant specific groups.

Admins always have full data access; impersonation/sandbox effects invisible to admins (test with non-admin account).

---

## Authentication & SSO

Docs: `people-and-groups/start`

| Method | Plan | User provisioning | Group sync | User attributes |
|--------|------|-------------------|------------|-----------------|
| Email/password | All | Manual invite | Manual | Manual (**Pro/Enterprise**) |
| Google Sign-In | All | Domain-restricted auto-create | No | No (use SAML/JWT) |
| LDAP | All | Default on | Mapping (**all plans**); membership filter (**Pro/Enterprise**) | Sync (**Pro/Enterprise**) |
| JWT | Pro/Enterprise | Default on | Optional sync + mappings | Yes |
| OIDC | Pro/Enterprise | Default on | Optional (groups claim) | Yes (claims) |
| SAML | Pro/Enterprise | Default on | Optional (custom attribute) | Yes (assertions) |
| SCIM | Pro/Enterprise | Decoupled from SSO auth | Okta: users+groups; Entra: users only | Via IdP |

**SSO disables password login** for that account once linked. Keep password auth enabled until SSO verified.

**2FA** (**Pro/Enterprise**): optional enforcement for password + LDAP logins only; SSO 2FA via IdP. Requires `MB_ENCRYPTION_SECRET_KEY` self-hosted.

**API keys**: Admin > Authentication; assigned to a **group** (inherits group permissions). Header: `X-API-Key`. Deleted group → keys reassigned to All Users. Pro/Enterprise self-hosted: config file creation.

### Google (`people-and-groups/google-sign-in`)
OAuth Client ID; authorized JS origin = Metabase URL. Domain field for auto-provisioning. Multiple domains (**Pro/Enterprise**).

### LDAP (`people-and-groups/ldap`)
Required attrs: email, first/last name. Group mapping syncs on **next login** (add/remove from mapped groups only). User filter default: `(&(objectClass=inetOrgPerson)(|(uid={login})(mail={login})))`.

### JWT (`people-and-groups/authenticating-with-jwt`)
Flow: `/auth/sso?jwt=TOKEN&return_to=...` (POST for modular embeds). Group sync via `groups` claim + mappings or name match. Disable password auth cautiously.

### OIDC (`people-and-groups/authenticating-with-oidc`)
Self-hosted: `MB_ENCRYPTION_SECRET_KEY` required. Redirect: `{site-url}/auth/sso/{key}/callback`. Group sync needs groups claim in ID token (provider-specific). Turn off auto-provision if using SCIM.

### SAML (`people-and-groups/authenticating-with-saml`)
ACS: `{site-url}/auth/sso`. SLO: `/auth/sso/handle_slo` (env vars). Group sync via custom attribute (e.g. `metabaseGroups`). Disable SAML auto-provision when using SCIM.

### SCIM (`people-and-groups/user-provisioning`)
Endpoint: `{site-url}/api/ee/scim/v2`. **Disables SAML auto-provision.** Okta: HTTP Header auth; Entra: users only.

---

## Permission types

Docs: `permissions/introduction`, `data`, `collections`, `application`

Set via Admin > Permissions (Cmd/Ctrl+K → Permissions).

### Data permissions (`permissions/data`)

Per database/schema/table:

| Type | Levels | Notes |
|------|--------|-------|
| **View data** | Can view, Granular, Row/column security, Impersonated, Blocked | OSS defaults Can view (UI hidden). Blocked overrides collection access |
| **Create queries** | QB+native, QB only, Granular | Requires Can view. Sandbox/Blocked on any table → **native disabled for entire DB** |
| **Download results** | No, Granular, 10k, 1M | Native downloads need whole-DB permission (no SQL parsing) |
| **Manage table metadata** | Yes/No/Granular | **Pro/Enterprise** |
| **Manage database** | Yes/No | Connection settings, sync/scan; not delete DB |
| **Transform** | Per database | **Pro/Enterprise**; requires View + QB+native on all tables |

**Blocked gotcha**: blocks viewing questions on that data even with collection access. Blocking **any** table blocks **all native SQL** on that database (Metabase can't parse SQL). Another group with Can view overrides Blocked.

**Hidden tables/columns/metadata visibility ≠ permissions** — SQL can still query them.

### Collection permissions (`permissions/collections`)

Curate / View / No access. Controls questions, dashboards, models, metrics, events, timelines — **not** query ability (needs data permissions).

Exception: **Blocked data** prevents viewing questions regardless of collection access.

Dashboard with cards from multiple collections: need View on **each** collection.

**Library > Data**: collection perms = navigation/picker only; **use data permissions for table access**.

### Application permissions (`permissions/application`) — Pro/Enterprise

- **Settings access**: Admin > Settings tabs (email, Slack, embedding, caching, etc.)
- **Monitoring access**: Monitor section (not dependency diagnostics — Data Analysts; alerts management — admins only)
- **Subscriptions and alerts**: who can create; set No to block All Users default

### Snippet folder permissions

Separate from collections. Docs: `permissions/snippets`

### Notification permissions (`permissions/notifications`)

- All Users can create subscriptions/alerts by default
- Recipients see data per **creator's** permissions (not recipient's)
- Impersonation/sandbox groups: **no Slack** subscriptions/alerts; email recipients list shows self only
- Admins can manage all subscriptions

---

## Data isolation methods

Docs: `permissions/data-isolation-methods`, `row-and-column-security`, `impersonation`, `database-routing`, `embedding`

### Row and column security (sandboxing) — Pro/Enterprise

Docs: `permissions/row-and-column-security`

- **Row**: filter column by user attribute (exact case-sensitive match)
- **Custom**: SQL question replaces table view (hide columns, multi-column filters, edited columns); save SQL in admin-only collection
- One policy per table/group; **multiple sandbox groups on same table = conflict error**
- **QB only** — native SQL bypasses sandbox (use collection No access on SQL questions with secured columns)
- **Public links bypass sandbox** — disable public sharing
- Doesn't apply to SQL question results; MongoDB/Druid: row only
- Sandbox groups: no Slack alerts/subscriptions
- Incompatible with model persistence

### Impersonation — Pro/Enterprise

Docs: `permissions/impersonation`

- DBs: ClickHouse, MySQL, Postgres (RLS on views: PG 15+), Redshift, Snowflake, SQL Server, Starburst/Trino
- View data = Impersonated at **database level**; user attribute → DB role (`SET ROLE`)
- Works for **both QB and native SQL** (single SELECT only; no CREATE/SET ROLE in user SQL)
- Connection user needs broad sync access; impersonated role has restricted privileges
- Snowflake: disable secondary roles on Metabase user
- Redshift: Metabase connection user must be superuser
- Admins unaffected; most permissive group overrides impersonation
- No Slack alerts/subscriptions

### Database routing — Pro/Enterprise

Docs: `permissions/database-routing`

- One router DB + destination DBs matched by user attribute slug
- Same schema required; build on router, query runs on destination
- **Not** with: writable connections, editable tables, actions, CSV uploads, model persistence, public links
- Guest embed: always routes to router (no user attributes)
- Admin without attribute sees router DB; invalid attribute = non-admin can't view

### Embedding permissions (`permissions/embedding`)

| Setup | Tool |
|-------|------|
| Commingled data, one DB | Row/column security or impersonation |
| One DB per customer | Database routing (+ sandbox/impersonation optional) |
| One schema/table per customer | Granular data permissions per table; separate DB connections for native SQL |

---

## Setup checklist for restricted access

1. **Block All Users** on database/schema/table
2. Create purpose-specific groups; never grant All Users more than baseline
3. Grant collection View/Curate per team
4. Choose isolation: sandbox (QB), impersonation (QB+SQL), or DB routing (multi-tenant DBs)
5. Block original tables if using transform/view substitutes for sandbox
6. Disable public sharing if sandboxing
7. Put sensitive SQL questions in admin-only collections
8. Test with non-admin test user (not admin — admins bypass impersonation/sandbox display)

---

## Plan summary

| Feature | OSS/Starter | Pro/Enterprise |
|---------|-------------|----------------|
| View data granular/blocked/sandbox/impersonation | No (implicit Can view) | Yes |
| JWT, SAML, OIDC, SCIM, 2FA | No | Yes |
| User attributes | No | Yes |
| Application permissions | No | Yes |
| Data Analysts group, Data Studio | No | Yes |
| Content verification, Official collections | No | Yes |
| Database routing | No | Yes |
| Group managers | No | Yes |
| LDAP advanced (group filter, attr sync) | No | Yes |
