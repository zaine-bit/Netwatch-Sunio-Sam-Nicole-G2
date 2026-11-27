# Device Management — Implementation Plan

## Purpose
Allow a signed-in Network Owner to maintain an inventory of devices registered to their network. This is an inventory feature; it does not discover devices automatically or collect live router traffic.

## User workflow
1. Open the Network Owner dashboard and choose My Devices.
2. View only devices registered under the signed-in account.
3. Add a device using fields confirmed by the approved ERD/SDD.
4. Open a device to review its saved details.
5. Edit or delete a device after a confirmation step.
6. Return to the list and see a clear success or validation message.

## Access and ownership rules
- Require the existing custom account session for every device page and action.
- Only a Network Owner may use owner device-management pages; an Administrator should be routed to the admin dashboard unless approved requirements explicitly grant broader access.
- Scope every read and write to the current account, conceptually Device.objects.filter(owner=request.account).
- For detail, update, and delete, retrieve the record through the owner-scoped queryset. Do not fetch an arbitrary device by ID and rely on hiding links in the template.
- A guessed ID belonging to another owner must not reveal the record; return the normal not-found response.
- Never accept an owner/account ID from a submitted form as authority. Set the relationship from the authenticated session on the server.
- Use POST for destructive actions and include CSRF protection.

## Form and validation plan
Exact fields and constraints must come from the approved ERD/SDD. Once confirmed:
- Mark required fields consistently in the form and server-side validation.
- Trim text input and validate lengths/types against the schema.
- Apply identifier uniqueness at the correct scope (global or per owner) only after confirming it.
- Show field-specific errors without losing valid submitted values.
- Use Django messages for successful create/update/delete actions.
- Do not invent MAC-address, IP-address, device-type, or uniqueness requirements before specified.

## Proposed page states
- Empty state: explain that no devices have been added and provide an Add Device action.
- List state: show each device's approved identifying fields and actions.
- Form state: add/edit form with inline errors and cancel navigation.
- Delete confirmation: identify the selected device using a safe display field and require explicit POST confirmation.
- Not found/unauthorized: do not expose another owner's data.

## Test plan
- Anonymous visitors are redirected to login for list/create/detail/update/delete.
- A Network Owner can create, list, view, update, and delete their own device.
- A second owner cannot list, view, update, or delete the first owner's device, including by guessing its URL ID.
- Submitted owner IDs cannot transfer ownership or create records for another account.
- An Administrator cannot access owner-only pages unless approved requirements say otherwise.
- Invalid and missing values are rejected according to the final schema.
- GET requests cannot perform deletion.
- Existing account registration, login, logout, profile, and role tests continue to pass.

## ERD/SDD decisions required before implementation
Confirm the device entity/table name, primary key, owner foreign key and delete behavior, all fields and data types, nullability, defaults, uniqueness/index rules, and relationships to usage or alert entities. No model or migration should be authored until these are agreed.
