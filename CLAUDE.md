# Vedel Servis: notes for AI assistants

Internal ops portal for Vedel Klima (sales, service, stock, crew, field) plus a public marketing site. The portal is Django under `backend/`. The marketing site is Next.js at the repo root (`src/`). Production portal: `https://servis.vedel.com.tr`. Local portal: `http://127.0.0.1:8000` via Docker Compose.

Faruk is the partner. UI copy is Turkish; public URL paths are English. Keep answers short and do the work.

## Always

- **English page URLs.** Paths are lowercase kebab-case English. Django URL *names* stay English (`portal-settings`). Never put Turkish in the path (`ayarlar`, `giris`, `cikis`). Before adding or renaming any page URL: stop, offer exactly **3** path options, wait for the pick. Do not invent a path in the meantime. No Turkish aliases unless asked. See `.cursor/rules/english-page-urls.mdc`.
- **Do not commit secrets.** Never commit `.env`, `.env.local`, credentials, keystores, or dump files that include passwords. `data-exports/` may hold business fixtures — treat as sensitive; don't push casually.
- **No commits / push / force-push** unless Faruk asks. Follow the repo git commit rules when he does.
- **Portal soft navigation.** List filters and service calendar day/month changes must not animate or hard-reload the whole `.workspace`. Prefer quiet soft swap / partial calendar swap (`data-sale-filters`, `data-day-swap`, `data-cal-month-swap` in `app_base.html`). If you change nav JS, verify typing and day clicks don't flicker.
- **Match existing portal UI.** Reuse `toolbar`, `toolbar-actions`, `btn` / `btn.is-ghost`, `fis-card`, `wait-card`, `device-serial`, `seg`, `field-label`, `sheet`. Avoid one-off inline styles. Outside `.fis` / `.wizard`, set `--fis-pad` on cards that use `var(--fis-pad)` (otherwise padding becomes `0`).
- **Temporary panels.** `/sales/mount-activation/` is a temporary backfill panel — keep it clearly temporary; don't wire it into permanent product flows without asking.
- Prefer changing the smallest surface that solves the request. Don't rewrite README/docs unless asked (except this guide when asked).

## Local portal (Django)

```bash
# from repo root
docker compose up -d          # db + backend → :8000
docker compose ps             # backend/db healthy
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py test <app_or_label>
```

- Compose file: `docker-compose.yml` (Postgres 16 + backend build from `backend/`).
- App code mounts at `./backend:/app`. Template/JS edits show after refresh (no rebuild for templates).
- Prod-like compose: `docker-compose.prod.yml` (binds `127.0.0.1:8020`, needs `.env`).
- Entry: `backend/entrypoint.sh`. Settings: `backend/vedelb2c/settings.py`.

Create a superuser only when needed:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Marketing site (Next.js)

Root `package.json` / `src/` — public site (vedel.com.tr). Local: `npm run dev` → usually `:3000`. Price sheet needs `PRICE_SHEET_URL` in `.env.local` (see `DEPLOY-SONRASI-MUTLAKA-OKU.md`). Don't mix Next routes into the Django portal.

## Apps (Django)

| App | Role |
|---|---|
| `accounts` | Auth, portal shell (`app_base.html`, sidenav, soft nav), users |
| `sales` | Parties, sales, payments, mount fields, mount-activation panel |
| `service` | Jobs, devices, schedule/browse calendar, field handoff |
| `stock` | Categories, products, movements |
| `crew` | Crew members / documents |

Templates live under `backend/accounts/templates/portal/`. Portal CSS/JS are largely inlined in `app_base.html` (+ `_mobile_css.html` / `_mobile_js.html`).

## Roles (high level)

Portal access is role-gated (`Customer` flags such as `can_sales`, `can_service_lead`, `can_service_field`, `can_stock`, `can_crew`, `can_users`). Side nav only shows what the user can open. Field (`/field/`) is a separate surface — soft-nav intentionally leaves it alone in places.

## Soft nav & flicker (critical)

`app_base.html` intercepts in-portal link clicks and swaps `.workspace` HTML. That is intentional for snappy navigation, but:

1. **Same-path filters** (`[data-sale-filters]`, live `q` search): quiet swap, no `is-leaving` / `is-arrive`; typing uses `history.replaceState` + focus restore; abort in-flight fetches.
2. **Service browse calendar**: day cells → `portalSwapDay` paint when data is in `day_panel`; otherwise / month ‹› → `swapServiceBrowse` (replace `.day-cal-row` + `.week-board` only). Never fall through to animated full `openPage` for those links.
3. **Side nav drill-ins**: Depo (`data-stock-open`) and Satış (`data-sales-open`) use a second pane (`has-drill` / `panes-2` / `panes-3`). Montaj aktivasyonu lives under Satış.

If flicker returns: check whether a click fell through to animated `openPage` or hard `location.href`, and whether `--fis-pad` / leave animation ran.

## Data pull / local load (no users)

Pull production **business** data into local Docker for realistic testing. Never dumps or overwrites `accounts` / `auth` / sessions.

```bash
# pull from fserver + load into local compose
./scripts/pull-prod-biz.sh --load

# pull only → data-exports/<stamp>/
./scripts/pull-prod-biz.sh

# reload latest (or a stamp) without re-pulling
./scripts/load-prod-biz.sh
./scripts/load-prod-biz.sh data-exports/20261113-2204
```

Includes: stock (categories/products/movements), sales (parties/sales/lines/payments), service (jobs/devices/photos/materials), crew (members/docs) + `media/`. Missing user FKs remap to a local user; `crew.user` links that don't exist locally are nulled. Login stays your local accounts. `data-exports/` is gitignored.

## Deploy

- Portal host: `servis.vedel.com.tr` (Docker / compose on the server; exact rsync/restart habit lives with Faruk — ask before touching prod).
- Marketing may use Fly / PM2 (`fly.toml`, `ecosystem.config.cjs`) — confirm before deploy.
- Never run destructive prod commands without an explicit ask.

## Test phase (how we verify)

Treat every non-trivial change as a short plan → code → prove cycle. Do not claim “done” without evidence.

### Before coding

1. Name the surface (sales / service / stock / field / shell).
2. Write 3–7 acceptance checks in chat (or a tiny checklist): happy path, one edge, one regression (flicker, URL, role).
3. Prefer a failing or extended unit test when the change is logic (mount, search İ/I, payments, stock cut). Pure CSS/layout can skip unit tests; still do a browser smoke.

### Automated (Django)

```bash
# full suite (expect green before deploy talk)
docker compose exec backend python manage.py test

# targeted
docker compose exec backend python manage.py test service.tests -k mount
docker compose exec backend python manage.py test accounts.tests_search
docker compose exec backend python manage.py test sales.tests
docker compose exec backend python manage.py test stock.tests
```

Modules: `backend/service/tests.py`, `backend/sales/tests.py`, `backend/stock/tests.py`, `backend/accounts/tests.py`, `backend/accounts/tests_search.py`.

Add or extend tests when changing: mount activation / `activate_sale_mount`, Turkish search, sale scheduling, field materials/stock, payments on close.

If the suite is red, fix or call out the failure before shipping related work. (Known risk area: sale-mount care interval defaults — re-check after interval UI changes.)

### Manual smoke (local :8000)

Run after shell / nav / filter / calendar / mount-panel work. Login as a user with the right roles.

| # | Check | Pass looks like |
|---|---|---|
| 1 | Soft nav | Side links swap workspace; no full white flash of chrome |
| 2 | Satış drill | Satış → pane → Montaj aktivasyonu opens; Menü returns |
| 3 | Live search | `/sales/` and `/sales/customers/` typing keeps focus; no leave/arrive flicker |
| 4 | Servis calendar | Day clicks paint list only; month ‹› swaps cal+jobs only; h1 stays |
| 5 | Mount panel | `/sales/mount-activation/` cards have padding; Fiş / Aktif et usable |
| 6 | Roles | Field user doesn’t see office-only controls; sales-only doesn’t see stock drill if denied |

Browser: Cursor IDE browser or Faruk’s machine. Prefer CDP/script checks for “leaving” class when debugging flicker.

### Data for local testing

- Prefer Docker DB with a recent `data-exports/` biz dump (users excluded, FKs remapped).
- Don’t invent fake prod customers on the live server for tests.
- Mount panel needs device sales without closed mount jobs — use local dump, not random prod writes.

### After coding (definition of done)

1. Targeted or full `manage.py test` output pasted or summarized (pass/fail counts).
2. Smoke table rows that apply are checked.
3. No new console/nav fallback to hard `location.href` on the happy path you touched.
4. Ask Faruk before prod deploy; after deploy, re-run the same smoke on `servis.vedel.com.tr` if he wants.

### Planning template (paste when starting a feature)

```
Amaç:
Dokunulan yüzeyler:
Otomatik testler:
Manuel smoke:
Risk (flicker / URL / rol / stok):
Prod’a çıkış: evet/hayır + Faruk onayı
```

## UI language

- Visible strings: Turkish.
- Code identifiers, URL paths, URL names, CSS class names: English.
- Money/date formatting: existing `portal_fmt` templatetags.

## What not to do

- Don't "fix" flicker by removing soft nav entirely unless asked.
- Don't add purple/cream AI-default marketing skins to the portal; keep the existing Vedel portal look.
- Don't invent new permanent nav items for temporary panels without asking.
- Don't paste secrets into chat replies or commit them.
