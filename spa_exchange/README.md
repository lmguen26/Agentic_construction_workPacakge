# Versioned SPA Exchange

This folder is the controlled drop zone for versioned building-datasheet SPAs and their downstream treatment.

## Lifecycle folders

```text
spa_exchange/
  generated/      # newly generated SPA versions awaiting distribution/review
  under_review/   # SPA copies currently assigned for human review
  reviewed/       # reviewer-completed SPA files with embedded review metadata
  extracted/      # machine-readable review_feedback JSON extracted from reviewed SPAs
  revised/        # regenerated/revised SPA versions after Agent R or deterministic updates
  archived/       # superseded SPA versions retained for audit/history
```

## Naming convention

Use immutable versioned filenames:

`<building_id>.datasheet.v<major>.<minor>.html`

Examples:
- `BLDG-001.datasheet.v1.0.html`
- `BLDG-001.datasheet.v1.1.html`
- `BLDG-001.datasheet.v2.0.html`

Never overwrite a reviewed or archived SPA. A revision creates a new version.

## Review loop

```text
generated/v1.0
  -> under_review/v1.0
  -> reviewed/v1.0
  -> extracted/v1.0.review_feedback.json
  -> Agent R / deterministic revision
  -> revised/v1.1
  -> under_review/v1.1
```

The reviewed SPA is the authoritative portable review package because it embeds both canonical site context and review metadata.

## Source-control guidance

This repository contains the folder structure and synthetic examples only. Real reviewed SPAs may contain sensitive operational information and should follow the approved storage/version-control policy in the deployment environment. If necessary, keep actual SPA instances outside Git while preserving the same folder convention locally or on an approved shared location.
