# Device Management — Acceptance and Test Plan

This plan is intentionally independent of database field names. Final model/form details must follow the approved ERD.

## User-facing behavior

A signed-in Network Owner can:
- Open a list of only their own registered devices.
- Register a device with the required details defined by the approved ERD.
- View a device's details.
- Edit a device they own.
- Delete a device they own, with the confirmation and related-record behavior defined by the approved design.

A visitor who is not signed in must be redirected to the login page. An Administrator must not gain access to an owner's private device records merely by having an administrator role; any separate administrative access must be explicitly required by the approved specification.

## Security and validation rules

- Derive the owner from the authenticated custom account/session. Never trust an owner ID submitted by the browser.
- Scope list and detail queries to the signed-in owner.
- For update and delete actions, verify ownership server-side before changing data.
- Validate required fields and field constraints from the ERD.
- Display understandable validation and success/error messages.
- Use POST for state-changing actions; do not delete records through a GET request.
- Do not expose another owner's device details in pages, forms, error messages, or redirects.

## Test cases

| ID | Scenario | Expected result |
|---|---|---|
| DEV-01 | Visitor opens device list | Redirect to login |
| DEV-02 | Owner opens device list | Only that owner's devices appear |
| DEV-03 | Owner submits valid device details | Device is saved and linked to the signed-in owner |
| DEV-04 | Owner submits missing/invalid required details | Form shows validation errors; no invalid record is saved |
| DEV-05 | Owner opens a device they own | Correct device details appear |
| DEV-06 | Owner edits a device they own | Changes are saved |
| DEV-07 | Owner attempts to view another owner's device | Access is denied or a not-found response is returned |
| DEV-08 | Owner attempts to edit/delete another owner's device | No change occurs; access is denied or not found |
| DEV-09 | Owner deletes their own device | Confirmation/redirect and deletion behavior match the approved design |
| DEV-10 | User submits a forged owner/account identifier | Server ignores it; ownership remains tied to the signed-in account |

## ERD/design confirmations needed

- Exact device fields, types, nullability, and validation constraints.
- Device identifier format and whether uniqueness is global or per owner.
- Required delete behavior when usage history or alerts already exist.
- Whether soft deletion is required.
- Any device status/type choices or other controlled values.

## Completion gate

Do not call this feature complete until automated tests cover the ownership boundaries and CRUD behavior, migrations apply cleanly to the configured PostgreSQL/Supabase database, and existing account tests still pass.
