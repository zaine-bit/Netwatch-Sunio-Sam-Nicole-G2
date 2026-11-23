# Daily Usage, Threshold Alerts, and Dashboard — Acceptance and Test Plan

This plan follows the approved scope: usage is entered or imported by the Network Owner (with sample/demo data where needed). It does not include live router collection, packet inspection, or automatic device blocking.

## User-facing behavior

- A signed-in Network Owner can record daily data usage for one of their own devices.
- The application retains usage history so that each device can be compared against its own historical average.
- The application flags unusually high usage using the threshold approved for the project.
- The owner dashboard presents device summaries, usage information, and alerts in plain language.
- Records and summaries are private to the owning account.

## Calculation behavior to implement and verify

The approved objective requires comparison with the device's own average, not a shared average across all devices. Before implementation, confirm these policy details with the approved SDD/ERD or project decision:
- Threshold value and unit (for example, percentage above average or a fixed amount).
- Whether the threshold is global, per owner, or per device.
- Which historical records count toward the average and the minimum history required before alerting.
- Whether the current day's record is excluded from its comparison baseline.
- How missing days, zero usage, edited records, and duplicate device/date records are handled.
- Whether alerts are persisted as database records, recalculated from usage history, or both.
- Whether repeated high-usage days create one alert or multiple alerts, and how alerts are acknowledged/resolved.

Do not silently choose these rules in code; document the approved decisions and test against them.

## Security and validation rules

- Require a valid custom-account login for usage entry and dashboard access.
- Resolve the device through a query scoped to the signed-in owner; never trust a device ID alone.
- Reject attempts to submit usage for another owner's device.
- Validate the usage amount, date, and other fields according to the approved ERD.
- Prevent invalid or negative usage values unless the approved specification explicitly defines otherwise.
- Use POST for record creation or edits and show clear validation/confirmation messages.
- Do not label manually entered, imported, or sample data as live router monitoring.

## Test cases

| ID | Scenario | Expected result |
|---|---|---|
| USE-01 | Visitor opens usage or dashboard page | Redirect to login |
| USE-02 | Owner records valid usage for their device | Usage is saved and linked to the correct device |
| USE-03 | Owner submits invalid usage amount/date | Validation error; no invalid record is saved |
| USE-04 | Owner submits a device belonging to another owner | Request is rejected; no record is created |
| USE-05 | Device has insufficient history for comparison | Behavior follows the approved minimum-history rule; no misleading alert |
| USE-06 | Usage exceeds the approved device-specific threshold | Alert/flag is produced according to the approved alert policy |
| USE-07 | Usage does not exceed the threshold | No high-usage alert is produced |
| USE-08 | Two devices have different usage histories | Each device is compared against its own history |
| USE-09 | Owner opens dashboard | Only their devices, usage summaries, and alerts appear |
| USE-10 | Owner changes a usage record | Average and alert state are updated consistently |
| USE-11 | Owner attempts to access another owner's usage/alert | Access is denied or not found |
| USE-12 | Sample/demo data is displayed | It is clearly identified as sample/demo data |

## Dashboard content checklist

- Clear device list and current/recent recorded usage.
- Historical usage context for each device.
- High-usage warning with the affected device and relevant date/value.
- Empty states explaining what to do when no devices or usage records exist.
- Clear labels that distinguish recorded/demo data from live network measurements.

## Completion gate

Do not call this feature complete until the approved calculation and alert policies are documented, automated tests cover calculations and owner isolation, migrations apply cleanly to PostgreSQL/Supabase, and existing account functionality still passes.
