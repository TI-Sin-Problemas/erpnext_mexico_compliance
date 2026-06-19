# AGENTS.md

## Quick start

```bash
# Install app (after bench/erpnext are set up)
bench get-app https://github.com/TI-Sin-Problemas/erpnext_mexico_compliance.git --branch version-16
bench --site site_name install-app erpnext_mexico_compliance

# Run tests (requires a full Frappe bench with MariaDB + Redis)
bench --site test_site run-tests --app erpnext_mexico_compliance
```

## Lint & format

- **Linter**: `ruff` (select F,E,W,I,UP,B,RUF) + `pre-commit` (ruff, eslint, prettier) + `semgrep` with frappe rules
- **Format**: Ruff (double quotes, tab indent, line-length 110)
- **CI**: lint runs via `pre-commit/action@v3` then `semgrep` and `pip-audit`

## Architecture

Frappe/ERPNext app (v0.13.0) for Mexican CFDI tax compliance.

| Directory | Purpose |
|-----------|---------|
| `overrides/` | Doctype class overrides (Customer, Employee, PaymentEntry, SalesInvoice, SalesInvoiceItem) |
| `controllers/` | `CommonController` base with CFDI stamp/cancel/email logic; `communication.py`, `queries.py`, `validators.py` |
| `ws_client/` | `APIClient` (extends `FrappeClient`) talking to a CFDI stamping web service |
| `sat/` | SAT catalog updater (downloads from `phpcfdi/resources-sat-catalogs` releases) |
| `utils/` | CFDI helpers, contacts, files, permissions |
| `patches/` | Migration patches (currently one in `0_13_0/`) |
| `fixtures/` | Custom Field, Property Setter, Cancellation Reason fixtures |

## Key constraints

- **Python >= 3.14**, **Frappe >=16.0.0,<17.0.0** (version-16 branch), **ERPNext >=16.0.0,<17.0.0**
- **Runtime deps**: `satcfdi==4.9.24`, `lxml==6.1.1` (build with `flit_core`)
- `typing-modules = ["frappe.types.DF"]` — use `frappe.types.DF` for DocType field type hints
- `export_python_type_annotations = True` in hooks — controllers get auto-generated annotations
- DocField field names use `mx_` prefix (e.g., `mx_stamped_xml`, `mx_uuid`, `mx_cfdi_use`)
- URLs in Chinese? No, they should be "RFC", "SAT", "CFDI" - Mexican tax terminology. All SAT doctypes use `key` as the link field name.
- Check `hooks.py` for the authoritative list of overrides, fixtures, and scheduler events
- SAT catalog Doctypes: `SAT CFDI Use`, `SAT Payment Option`, `SAT Payment Method`, `SAT Product or Service Key`, `SAT Relationship Type`, `SAT Tax Regime`, `SAT UOM Key`, `Cancellation Reason`
- Scheduler: `check_cancellation_status` runs hourly

## CI quirks

- Tests use `partial-restore` from `.github/helper/partial-database.sql.gz` before running
- CI spins up MariaDB 11.8 + Redis (cache + queue) as services
- The `bench init` uses `--frappe-branch version-16 --skip-redis-config-generation --skip-assets`
- `dependabot` checks pip deps daily and GitHub Actions weekly

## Style notes

- Ruff config in `pyproject.toml` (not `.ruff.toml`)
- `__init__.py` only contains `__version__ = "0.13.0"`
- All modules use module-level docstrings (license header)
- Uses `pypika` for SQL construction in `sat/catalogs.py` (not `frappe.qb` in one file)
- Contains a sys.path workaround for `frappe#27373` in `overrides/sales_invoice.py`
