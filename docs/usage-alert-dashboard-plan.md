# Daily Usage, Threshold Alerts, and Dashboard — Implementation Plan

## Purpose and scope
Netwatch records daily data-usage values for a Network Owner's registered devices. It compares a device's new usage with that same device's historical average and presents a simple warning when the configured threshold is exceeded.

Values are manually entered, imported, or clearly labelled demonstration data. This feature does not inspect packets, connect to routers, block devices, or claim to monitor live traffic.

## Daily usage workflow
1. A signed-in Network Owner chooses one of their registered devices.
2. They enter a usage value and usage date using fields and units defined by the ERD/SDD.
3. The server validates the value and verifies that the selected device belongs to the current account.
4. The saved record becomes part of that device's history.
5. The dashboard refreshes the device summary, history, and any applicable warning.

The exact units (for example MB or GB), precision, whether one record per device per date is allowed, and whether records can be edited/imported must be confirmed before implementation.

## Average and threshold behavior

### Proposed transparent rule
For a device with prior valid daily usage records:
- Calculate that device's historical average from its eligible earlier records.
- Compare the new daily value with that average.
- A warning is eligible when the new value is greater than the average multiplied by the configured factor.

For a percentage threshold T, the proposed comparison is:
new_usage > historical_average × (1 + T / 100)

Example only: if the historical average is 2 GB and the threshold is 50%, a new value above 3 GB is flagged. Equality is not flagged under this proposed strict-greater-than rule.

### Decisions to confirm
- The threshold value and whether it is global, per owner, or per device.
- Whether the current day's record is excluded from the baseline (recommended to avoid comparing a value against an average that already includes itself).
- Minimum number of historical days required before evaluating an alert.
- Whether zero-usage days count in the average.
- Whether edited/deleted usage records recalculate an existing alert.
- Whether an alert is stored as a database record or derived when results are requested.
- Whether alert status can be acknowledged/resolved and whether repeated alerts are deduplicated.

Do not implement a guessed threshold or persist alerts before the ERD/SDD defines the data model.

## Dashboard information architecture
Proposed Network Owner dashboard sections:
1. Overview — count of registered devices and a concise total for the selected day/period, if supported by the data model.
2. Device usage — each device's latest recorded value and a comparison with its own baseline.
3. Alerts — clear warnings identifying the device, recorded date/value, baseline, and reason.
4. Recent records — latest daily entries with date, device, and usage.
5. Actions — add/manage devices and record daily usage.

Use plain labels and explain that values are recorded/imported, not collected live. Provide empty states when no devices, history, or alerts exist. Avoid charts or percentages that imply data not actually stored.

## Security and validation
- All pages/actions require the existing custom account session.
- Every usage query must be scoped through a device owned by the signed-in account.
- Never trust a submitted device ID or owner ID without checking ownership server-side.
- Reject negative values and invalid dates; apply precision and range limits only after units/schema are confirmed.
- Enforce any one-record-per-day rule in validation and the database only if approved.
- Do not let one owner view another owner's usage or alerts, including through guessed IDs.

## Test plan
- A user cannot record usage for another owner's device.
- A user cannot view another owner's history or alerts.
- Invalid, negative, missing, and out-of-range values are rejected according to the final schema.
- The average uses only the correct device's eligible historical records.
- The current record is excluded from its own baseline if that rule is approved.
- Threshold boundary tests cover below, equal to, and above the threshold.
- Insufficient history produces no misleading alert.
- Editing/deleting a record updates derived summaries/alerts according to agreed behavior.
- Empty dashboard states render correctly.
- Existing account and device-ownership tests remain green.

## ERD/SDD decisions required before implementation
Confirm usage and alert entities, fields, data types, units, foreign keys, delete behavior, uniqueness rules, threshold storage, alert persistence/status, and relationships between Account, Device, Usage, and Alert. No models, migrations, or database-backed feature views should be written until those decisions are confirmed.
