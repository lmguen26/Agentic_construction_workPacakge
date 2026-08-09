# Repository Copilot Instructions

This repository models an auditable, human-in-the-loop, building-level construction work-package pipeline.

## Read first

Before major architecture, onboarding, mapping or orchestration work, read:

1. `docs/CANONICAL-CONVENTIONS.md`
2. `docs/identity-and-occupancy-model.md`
3. `docs/MASTERCLASS-COOKBOOK.md`
4. `docs/model-selection-guide.md`

When older examples conflict with current contracts or `CANONICAL-CONVENTIONS.md`, do not copy the legacy convention forward.

## Global rules

- Never fabricate missing source data.
- Treat deterministic blocking validation failures as blocking.
- Preserve source identifiers, effective dates and lineage through every stage.
- Prefer structured JSON artifacts over free-form prose between stages.
- Do not silently modify upstream facts.
- Separate deterministic calculations from LLM interpretation.
- Record assumptions, exceptions and confidence where applicable.
- Business rules belong in `/rules` and must be referenced by version.
- Final recommendations require human review before publication.
- The physical building/premises analysis unit is identified by `building_id`.
- `site_id` is a parent location grouping; a transit/service point is a business identity. Do not collapse these identities.
- New stage artifacts use the canonical `stage` field, not legacy `pipeline_state`.

## Real-data onboarding

Use **Agent M - Data Onboarding Facilitator** before live analysis when connecting real operational data.

Agent M should guide source-by-source mapping and explicitly resolve:

- Region / Branch / Site / Building hierarchy;
- transit/service-point identity;
- temporal occupancies;
- mixed owned/leased tenure;
- lease-to-occupancy relationships;
- source-field mappings and identifier crosswalks.

Do not run live Agent A until one pilot `site_context.json` is trusted and human-confirmed.

## Model-selection reminder

Before a major task, identify the task type and remind the user which model class is preferred. Read `docs/model-selection-guide.md`.

Default guidance when those models are available in the current GitHub Copilot environment:

- **Claude Opus / strongest reasoning model:** repository comprehension, Agent M real-data onboarding, semantic source mapping, identity/occupancy ambiguity, architecture review, early Agent B/T validation.
- **Codex / strongest coding model:** Python adapters, validators, schemas, tests, orchestration, refactoring and debugging after semantic decisions are explicit.
- **Gemini / different model family:** independent challenge, second opinion, large-context cross-check and adversarial review of recommendations produced by another model family.
- **Deterministic Python:** authoritative calculations and validations whenever practical, especially Agent C cost arithmetic.

Do not permanently bind an agent role to a vendor/model. Model names and availability change. Keep contracts, rules and evaluators model-agnostic and record the actual model used in run metadata.

## Analysis control

The current pipeline is configured by `analysis_manifest.json`.

Profiles:

- `LEVEL_0_VALIDATION`
- `LEVEL_1_WORK_PACKAGES`
- `LEVEL_2_STRATEGIC`
- `LEVEL_3_ADVANCED`
- `CUSTOM`

A multi-building cockpit selection creates multiple independent building manifests/runs. Do not combine them into a subportfolio recommendation inside this repository.

## Pipeline

0. **Agent M / onboarding when required:** map real sources to canonical data with human-approved associations.
1. **Deterministic Data Quality Gate:** verify source readiness, associations and applicability.
2. **Site Context Builder:** create one canonical `site_context.json` for one physical `building_id`.
3. **Analysis Manifest:** define requested depth, effort and enabled capabilities.
4. **Agent A:** normalize deficiencies into opportunities.
5. **Agent B:** cluster opportunities and form candidate work packages using SALVO-inspired bundling/blending logic.
6. **Agent C + deterministic cost engine:** calculate/interpret approved cost indexation and indirect costs without changing scope.
7. **Agent T:** formulate strategic recommendations from authorized evidence/rules.
8. **Agent E:** produce an executive synthesis without creating/restructuring work packages.
9. **SPA generator:** render structured outputs into a versioned building datasheet.
10. **Human review:** capture reviewer decisions and metadata in the SPA.
11. **Agent R / revision routing:** process structured reviewer feedback into controlled revisions and new SPA versions.

## Artifact discipline

Each stage must:

- declare its expected input artifact;
- validate that the upstream stage is complete and authorized by the manifest;
- produce only its declared output artifact;
- preserve IDs linking results to original records;
- use `building_id` as the required physical analysis identity in new A/B/C/T/E artifacts;
- include transformation/model/rule metadata where applicable;
- stop when required information is missing or relationships are unresolved at blocking severity;
- never use an LLM to compensate for a deterministic association error.

## Legacy warning

`contracts/site-validation.schema.json` and some old generated V0.2 reference fixtures are retained for historical compatibility but are deprecated conventions. New work should use the Data Quality Gate in `site_context.json`, `analysis_manifest.json`, current stage contracts, and `pipeline-run.schema.json`.