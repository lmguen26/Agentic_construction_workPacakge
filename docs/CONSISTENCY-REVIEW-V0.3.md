# V0.3 Consistency Review

## Purpose

This review was performed after the repository expanded from an Agent A test harness into a configurable building-analysis, real-data onboarding, human-review and revision workflow.

The objective was to remove contradictions caused by incremental evolution without redesigning the solution.

## Canonical decisions confirmed

### Analysis unit

One pipeline run analyzes one physical building/premises and uses `building_id` as the required identity.

A batch selection can contain many buildings, but creates independent building manifests/runs.

### Hierarchy and business identity

Selection hierarchy:

`Region -> Branch -> Site -> Building`

Business occupancy relationship:

`Transit/Service Point <-> Temporal Occupancy <-> Building/Premises <-> Lease where applicable`

Transit/service-point identity is not a physical building/site identity and may move over time.

### Mixed tenure

A site can contain both owned and leased physical portions. Premises/building-portion data are optional until real onboarding demonstrates the explicit layer is necessary.

### Stage artifacts

Current A/B/C/T/E artifacts use:

- required `building_id`;
- optional parent `site_id`;
- canonical `stage` field.

Legacy use of `site_id` as a building identifier and `pipeline_state` as the stage field is deprecated.

### Stage ownership

- M: guided real-data onboarding/mapping
- Data Quality Gate: deterministic readiness/relationship validation
- A: deficiencies -> opportunities
- B: work-package creation / bundling / blending
- C: deterministic costing interpretation
- T: strategic recommendation
- E: synthesis only
- SPA: human review interface
- R: controlled review-driven revision/routing
- Orchestrator: traffic control driven by the manifest

### Analysis control

`analysis_manifest.json` controls Level 0/1/2/3/Custom and Rapid/Standard/Thorough configuration.

Level 0 does not invoke Agent A.

### Review

Review is performed in the HTML SPA. Reviewer metadata are embedded as structured JSON. Reviewed artifacts are versioned and not overwritten.

### Real-data onboarding

Agent M must establish trusted source mappings and identity relationships before live agent analysis. The first production milestone is one trusted, human-confirmed real `site_context.json`.

## Files aligned during this review

The review aligned or clarified:

- `README.md`
- `.github/copilot-instructions.md`
- `.github/agents/orchestrator.agent.md`
- `.github/agents/agent-b-workpackage.agent.md`
- `.github/agents/agent-c-cost.agent.md`
- `.github/agents/agent-t-strategy.agent.md`
- `.github/agents/agent-e-summary.agent.md`
- `.github/prompts/build-site-context.prompt.md`
- `contracts/opportunities.schema.json`
- `contracts/workpackages.schema.json`
- `contracts/costed-workpackages.schema.json`
- `contracts/recommendations.schema.json`
- `contracts/building-summary.schema.json`
- `contracts/site-context.schema.json`
- `contracts/analysis-manifest.schema.json`
- `contracts/pipeline-run.schema.json`
- `contracts/source-catalog.v0.2.json`
- `contracts/site-validation.schema.json` (explicitly deprecated)
- `src/costing/cost_engine.py`
- `src/quality/data_quality_gate.py`
- `src/evaluation/agent_a_live_evaluator.py`
- `src/evaluation/reference_fixture_builder.py`
- relevant evaluator tests
- `docs/information-model-v0.2.md`
- `docs/selection-hierarchy.md`
- `docs/pipeline-workflow.md`

`docs/CANONICAL-CONVENTIONS.md` was added as the normative compact source of truth.

## Important corrections made

### Fixed legacy identity misuse

Earlier contracts used `site_id` while actually storing a building ID. Current contracts now require `building_id` and keep `site_id` only as optional parent context.

### Fixed stage naming

Reference fixtures used `pipeline_state` while schemas/agents used `stage`. Current generated/reference logic now uses `stage`.

### Fixed Agent B contract mismatch

The B schema and B instructions now share the same canonical field vocabulary for opportunity IDs, rationale, bundle type, scope, dependencies/conflicts and optional base-cost inputs.

### Fixed Agent C contract mismatch

The deterministic cost engine, C instructions and cost contract now use consistent cost fields: direct cost, indexation factor, indexed direct cost, indirect cost, contingency and total cost.

### Fixed Agent T contract mismatch

The recommendation contract now uses `recommended_action`, `timing`, `rationale`, evidence lineage and human-review flags consistently with Agent T.

### Fixed Agent E contract mismatch

The summary contract and E instructions now use building identity and a consistent `work_package_summary` structure. E remains a synthesis stage, not a second work-package generator.

### Fixed orchestrator obsolescence

The orchestrator previously expected legacy `site_validation.json` and an unconditional A->E sequence. It now uses the Data Quality Gate, `site_context.json`, `analysis_manifest.json`, configurable profiles, SPA review and Agent R revision.

### Fixed mixed-tenure assumption in Data Quality Gate

The gate now uses premises-level tenure when available and falls back to building-level `ownership_type` only for simple/legacy datasets.

## Deliberate compatibility decisions

Some filenames retain historical version labels (`information-model-v0.2.md`, `source-catalog.v0.2.json`) so links/history are not broken. Their content now states the current convention.

`contracts/site-validation.schema.json` remains in the repository only as an explicitly deprecated compatibility artifact.

## Normative precedence

Use:

1. current JSON contract;
2. `docs/CANONICAL-CONVENTIONS.md`;
3. `docs/identity-and-occupancy-model.md` for identity/time/tenure;
4. current specialist-agent instruction;
5. Masterclass / implementation docs;
6. historical examples.

## Verification when cloned locally

Because GitHub connector editing does not execute the repository test suite, run the following after cloning/pulling the branch:

```bash
python -m pytest -q
```

Then regenerate synthetic reference artifacts if desired using the current reference fixture builder.

The first real-data deployment should additionally validate one pilot building end-to-end through:

`mapping -> canonical data -> Data Quality Gate -> site_context.json -> human confirmation`

before any live Agent A execution.
