# Canonical Conventions — Repository Source of Truth

## Purpose

This document resolves naming and architectural conventions that evolved across V0.1–V0.3. When older examples, generated fixtures or historical documentation conflict with this document, **this document and the current JSON contracts take precedence**.

The repository is evolving rapidly; this file exists so humans and Copilot have one short normative reference.

## 1. Atomic analysis unit

The atomic execution, recommendation, SPA review and revision unit is the **physical building / physical premises analysis unit** identified by:

`building_id`

A batch selection may include many buildings, but each building gets its own:

- Data Quality Gate result;
- `site_context.json`;
- `analysis_manifest.json`;
- A/B/C/T/E artifacts;
- SPA;
- review metadata;
- revision history;
- pipeline-run record.

One batch selection may therefore create many independent building runs.

## 2. Selection hierarchy

The user-facing selection hierarchy is:

```text
Region -> Branch -> Site -> Building / physical premises
```

Canonical hierarchy identifiers:

- `region_id`
- `branch_id`
- `site_id`
- `building_id`

`site_id` is a parent location/logical grouping. It must not be used as a substitute for `building_id` in building-stage artifacts.

## 3. Transit / service-point identity

A transit number / service point is a **business identity**, not a permanent physical identifier.

Canonical concepts:

- `service_point_id`: canonical business/service-point identifier;
- `transit_id` or source transit number: source/business identifier where applicable;
- `occupancy_id`: temporal relationship connecting the business identity to physical premises.

A transit can move from building to building over time. Multiple transits can coexist at one site.

Therefore:

```text
transit_id != site_id
transit_id != building_id
service_point_id != building_id
```

Current and historical location must be resolved through dated occupancy relationships.

See `docs/identity-and-occupancy-model.md`.

## 4. Mixed tenure

A site may contain owned and leased portions simultaneously.

Do not assume:

```text
one site = one tenure type
```

When real data requires explicit physical subdivision, a `premises` / `building_portion` layer may be introduced. This layer is optional until real-data onboarding proves it is required.

A lease belongs to the applicable leased occupancy/premises relationship, not automatically to the entire site or building.

## 5. Canonical stage identity fields

Current A/B/C/T/E contracts use:

- top-level `building_id` as the required analysis identity;
- optional `site_id` as parent context;
- `stage` as the canonical stage-state field.

Do not use legacy patterns where `site_id` contains a building ID or where `pipeline_state` replaces `stage` in new artifacts.

Canonical stages:

```text
OPPORTUNITIES
CLUSTERED
COSTED
RECOMMENDED
SUMMARIZED
```

Validation/review/revision state is tracked separately by the Data Quality Gate, pipeline-run metadata and review records.

## 6. Agent ownership

- **Agent M** — guided real-data onboarding and mapping facilitator; does not finalize ambiguous mappings without human approval.
- **Validator / Data Quality Gate** — deterministic source readiness and relationship validation.
- **Agent A** — deficiency -> opportunity normalization.
- **Agent B** — clusters, bundling/blending and work-package creation.
- **Agent C** — uses/interprets deterministic costing; authoritative arithmetic stays deterministic wherever possible.
- **Agent T** — strategic recommendation.
- **Agent E** — executive synthesis only; does not create/restructure work packages.
- **SPA** — human-facing reviewed information product with embedded structured metadata.
- **Agent R** — controlled reviewer-feedback revision/routing.
- **Orchestrator** — traffic control; reads the manifest, enforces gates/stage ownership and does not become a super-agent.

## 7. Analysis control

The pipeline is configured by `analysis_manifest.json`.

Profiles:

- `LEVEL_0_VALIDATION`
- `LEVEL_1_WORK_PACKAGES`
- `LEVEL_2_STRATEGIC`
- `LEVEL_3_ADVANCED`
- `CUSTOM`

Effort:

- `RAPID`
- `STANDARD`
- `THOROUGH`

Effort settings must eventually have explicit methodological behavior; they are not simply LLM reasoning-effort adjectives.

## 8. Data-quality vocabulary

Source/domain quality states:

- `COMPLETE`
- `PARTIAL`
- `CONFLICT`
- `STALE`
- `NOT_APPLICABLE`
- `MISSING`

Issue severity:

- `BLOCKING`
- `WARNING`
- `INFORMATIONAL`

Overall canonical context status:

- `VALIDATED`
- `REVIEW_REQUIRED`
- `BLOCKED`

`unknown`, `missing`, `not applicable`, and numeric zero are distinct concepts and must never be collapsed.

## 9. Detention terminology

Use **detention horizon / horizon de détention**.

Canonical field:

`detention_horizon_years`

Canonical bands:

- `LT_2_YEARS`
- `2_TO_5_YEARS`
- `GT_5_YEARS`
- `UNKNOWN`

Do not use `retention_horizon`.

## 10. Source-to-canonical integration

Operational source schemas remain unchanged where practical.

```text
Operational source
 -> mapping
 -> crosswalk / deterministic transformation
 -> canonical model
 -> Data Quality Gate
 -> site_context.json
```

Mappings describe fields. Crosswalks resolve identifiers or controlled values. LLMs may propose mappings, but authoritative identity association must be deterministic/human-approved.

## 11. Strategic context

`strategic_context` is optional, high-value qualitative evidence from structured transcription or similar authorized sources.

It may influence Agent T reasoning but cannot silently overwrite authoritative facts such as lease dates, building attributes, projects, costs or detention horizon.

## 12. Work-package and cost ownership

Agent B creates the work-package structure. Agent C does not change scope.

Cost terminology in the current contract includes:

- `direct_cost`
- `indexation_factor`
- `indexed_direct_cost`
- `indirect_cost`
- `indirect_costs`
- `contingency`
- `total_cost`
- `calculation_trace`

Cost rule/table versions must be traceable. LLMs do not invent authoritative rates.

## 13. Recommendation terminology

Agent T uses:

- `recommendation_id`
- `work_package_id`
- `recommended_action`
- `timing`
- `rationale`
- `dependencies`
- `constraints`
- `risks`
- `alternatives`
- `assumptions`
- `exceptions`
- `evidence_lineage`
- `human_review_required`

Avoid introducing synonymous fields such as `recommendation` or `proposed_timing` into new artifacts unless the contract is deliberately versioned.

## 14. Human review and versioning

Review occurs through the HTML SPA.

The SPA embeds structured review metadata including reviewer identity, timestamps, decisions, comments, confirmation and audit events.

Reviewed artifacts are never overwritten. The lifecycle is:

```text
generated -> under_review -> reviewed -> extracted -> revised -> archived
```

Reviewer comments are structured feedback. A comment that contradicts source data routes to source correction rather than silently modifying the canonical fact.

## 15. Real-data onboarding

Before any live Agent A run:

1. understand the repository;
2. identify real sources;
3. map attributes;
4. resolve identity relationships;
5. validate mappings/crosswalks;
6. create canonical data;
7. run the Data Quality Gate;
8. inspect one trusted real `site_context.json`;
9. obtain explicit human confirmation;
10. then activate Agent A.

Agent M is the facilitator for this process.

## 16. Model selection

The architecture is model-agnostic. Current task-based recommendations are documented in `docs/model-selection-guide.md`.

General pattern:

- strongest reasoning model for semantic onboarding/architecture/high-ambiguity B/T work;
- coding-specialized model for implementation/tests/refactoring;
- a different model family for independent challenge;
- deterministic code for authoritative calculations and validations.

Record the actual model used when possible; never encode methodology as vendor-specific behavior.

## 17. Product boundary

This repository produces **reviewed building-level work-package information products**.

It is not the portfolio optimization engine.

Future portfolio/scenario tooling can consume approved building work packages to perform annual CAPEX constraints, prioritization, optimization, capacity planning and multi-year portfolio scheduling.

## 18. Legacy artifacts

Historical V0.1/V0.2 files may remain for traceability. In particular:

- `contracts/site-validation.schema.json` is deprecated;
- old generated reference fixtures may use `site_id` as a building identifier or `pipeline_state` as a stage field.

Do not copy those conventions into new production integration. Regenerate reference fixtures from current builders when practical.

## Normative precedence

When there is ambiguity, use this precedence:

1. current JSON contract for the artifact being produced;
2. this `CANONICAL-CONVENTIONS.md` document;
3. `identity-and-occupancy-model.md` for identity/tenure/time questions;
4. current specialist-agent instructions;
5. Masterclass/Cookbook and implementation documentation;
6. historical examples/legacy fixtures.

If these sources genuinely disagree after applying this order, stop and document the conflict rather than silently choosing a convention.