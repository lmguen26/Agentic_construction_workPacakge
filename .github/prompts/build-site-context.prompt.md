---
description: Prepare and review the deterministic canonical building site context before any downstream agent run.
agent: Work Package Orchestrator
---

Prepare the selected physical `building_id` for the configured analysis pipeline.

1. Read `docs/CANONICAL-CONVENTIONS.md` and `docs/identity-and-occupancy-model.md` when real identity/tenure data are involved.
2. Run or inspect the deterministic Site Context Builder output.
3. Confirm `site_context.json` conforms to `contracts/site-context.schema.json`.
4. Confirm the context `building_id` is the physical analysis identity and that parent `site_id` / transit-service-point identifiers have not been substituted for it.
5. Confirm `data_quality.status` is not `BLOCKED` and review Data Quality Gate results.
6. Review association exceptions, temporal occupancy warnings, lease/premises conflicts and multi-occupant conditions.
7. Confirm `detention_horizon_years` and `detention_band` use canonical detention terminology.
8. Preserve `unknown`, `missing`, `not applicable`, and zero as distinct states.
9. Do not infer missing source facts or repair ambiguous identifiers with fuzzy matching silently.
10. Confirm an `analysis_manifest.json` exists before starting a configured analysis run.
11. If the manifest is `LEVEL_0_VALIDATION`, stop after context/datasheet preparation; do not invoke Agent A.
12. If the manifest authorizes work-package analysis and no blocking issue remains, offer the Agent A handoff.

The canonical `site_context.json`, not raw source tables or a legacy `site_validation.json`, is the factual input to Agent A.