# Phase 2 Preparation Notes

## Project direction

Netwatch helps a Network Owner identify which of their own devices is using unusually high data. Usage is entered or imported by the owner; this phase does not implement live router or packet-level monitoring.

## Phase 1 code audit (develop)

Reviewed the current account model, views, URLs, login decorator, account tests, migrations, owner dashboard template, base template, settings, and Git ignore rules.

- The custom `accounts.Account` model stores the Network Owner / Administrator role and account profile fields.
- Registration hashes passwords with Django's `make_password`; login checks them with `check_password`.
- The custom session stores `account_id`; `account_login_required` resolves an active account and clears invalid sessions.
- Owner and Administrator dashboard routing is already present.
- The owner dashboard is currently a placeholder, ready for the Netwatch device and usage overview.
- The current test file has five account-focused tests. Before feature integration, expand coverage for profile ownership, logout, inactive accounts, admin restrictions, and the new feature ownership rules.
- `.env` and virtual-environment directories are ignored by Git. Keep secrets out of commits.

## Phase 2 feature breakdown

### Feature A: Device Management
- Let a signed-in Network Owner add, view, edit, and delete their devices.
- Every device must be associated with its owning account.
- Enforce ownership in server-side queries and view actions, not only in the interface.
- Validate required device details and prevent another owner from viewing or changing the record.

### Feature B: Daily Usage, Threshold Alerts, and Dashboard
- Record daily usage against a device and date.
- Build a device-specific historical average.
- Compare a new usage record against that device's average using a configurable threshold.
- Show device summaries, usage history, and alerts in a clear owner dashboard.
- Use clearly labelled sample/demo records where appropriate; do not imply live router collection.

## ERD-dependent work (do not implement yet)

Wait for the approved ERD/SDD before creating or changing database models and migrations. Confirm:
- Entity and field names, types, and required/optional fields.
- Whether devices, usage records, and alerts have the expected foreign-key relationships.
- Delete behavior and uniqueness rules (for example, whether a device identifier must be unique per owner).
- Where the threshold is stored and whether it is global or per device.
- Whether an alert is stored as a record or derived when the dashboard is loaded.

## Proposed implementation order

1. Confirm the ERD and align the model design.
2. Implement Device Management and its ownership/validation tests.
3. Implement daily usage recording and historical calculations.
4. Implement threshold alert creation/handling and dashboard summaries.
5. Run migrations and tests against the configured PostgreSQL/Supabase database.
6. Verify existing registration, login, logout, profile, and role restrictions still work.

## Git workflow

Create each feature branch from `develop`, open a pull request into `develop`, and integrate tested features there. Merge `develop` into `main` only after the phase is ready. Do not commit feature work directly to `main`.
