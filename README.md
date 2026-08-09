# Agentic Construction Work Package

Synthetic reference architecture for a configurable, human-in-the-loop, **building-level analysis workflow within a Region -> Branch -> Site hierarchy**. The solution transforms validated building information into normalized opportunities, clusters, work packages, costed work packages, recommendations, executive summaries, reviewable HTML SPAs, and structured revision feedback.

> Do not commit confidential operational data, production prompts, pricing tables, credentials, or real datasets to this public repository.

## Start here

**Canonical source of truth:** [`docs/CANONICAL-CONVENTIONS.md`](docs/CANONICAL-CONVENTIONS.md). Use it when older examples or historical V0.1/V0.2 material conflicts with the current architecture.

**New to the methodology?** Read [`docs/MASTERCLASS-COOKBOOK.md`](docs/MASTERCLASS-COOKBOOK.md). It explains the business concepts, deterministic/agentic boundaries, every phase and agent, the cockpit, analysis levels, human review, revision loop, governance, common failure modes, and complete step-by-step operating recipes.

**Deploying with real work data?** Read [`docs/COPILOT-WORK-ONBOARDING.md`](docs/COPILOT-WORK-ONBOARDING.md), [`docs/identity-and-occupancy-model.md`](docs/identity-and-occupancy-model.md), and [`docs/model-selection-guide.md`](docs/model-selection-guide.md).

## Product objective

The repository supports repeatable analysis of physical buildings/premises **individually**, producing reviewed and traceable building-level work-package information products. A user may select many buildings at once, but the batch is an operational convenience: each building receives an independent manifest, run, SPA, review and revision history.

The repository intentionally stops short of portfolio optimization. A future portfolio/scenario solution can consume approved building-level work-package information products downstream.

## Identity model in one sentence

`Region -> Branch -> Site -> Building` is the selection hierarchy, while `Transit/Service Point <-> Temporal Occupancy <-> Building/Premises <-> Lease where applicable` is the business-occupancy relationship.

A transit can move over time; it is never a substitute for `building_id` or `site_id`. A site may also contain owned and leased portions simultaneously.

## Core workflow

```text
Operational source data
        |
        v
Agent M guided onboarding / mappings / crosswalks when connecting real data
        |
        v
Canonical Data Model
        |
        v
Deterministic Data Quality Gate
        |
        v
Canonical site_context.json for one building_id
        |
        v
Configurable analysis_manifest.json
        |
        v
[A] Opportunity normalization
        |
        v
[B] SALVO-inspired clustering / bundling / blending
        |
        v
[C] Deterministic costing + bounded interpretation
        |
        v
[T] Building/site strategic recommendation
        |
        v
[E] Executive synthesis
        |
        v
Versioned HTML SPA building datasheet
        |
        v
Human review + embedded review metadata
        |
        v
Structured review feedback
        |
        v
[R] Controlled revision / routing
        |
        v
New SPA version / further review
```

## Analysis profiles

- **Level 0 — Validation only:** deterministic source readiness and site-context generation.
- **Level 1 — Work Package Analysis:** core A-B-C-T-E pipeline.
- **Level 2 — Strategic Site Analysis:** adds lease/occupancy, detention horizon, initiatives/projects, accessibility, lifecycle, risk, FCI/replacement value and strategic context when available.
- **Level 3 — Advanced Investment Analysis:** adds cost sensitivity, amortization, alternatives and timing analysis.
- **Custom:** user-selected capability combination.

Analysis effort is a separate dimension: `RAPID`, `STANDARD`, or `THOROUGH`.

## Model selection

The methodology is model-agnostic, but the default task routing is:

- **Claude Opus / strongest available reasoning model:** semantic onboarding, Agent M, architecture comprehension, difficult identity/occupancy mapping, and early B/T validation.
- **Codex / strongest available coding model:** adapters, deterministic validators, schemas, tests, orchestration, debugging and refactoring.
- **Gemini / different model family:** independent challenge, second opinion and adversarial review.
- **Deterministic Python:** authoritative calculations and validation whenever practical, particularly costing arithmetic.

See `docs/model-selection-guide.md`. Actual model used should be recorded in run metadata; agents should not be permanently bound to one vendor/model.

## Desktop application

Run:

```bash
python app/main.py
```

The desktop application provides hierarchical multi-filter selection (`Region -> Branch -> Site -> Building`), multi-building batch scope, validation, site-context generation, HTML datasheet generation and access to the **Site Analysis Cockpit**. Batch operation preserves independent per-building artifacts and review histories.

The cockpit produces a versioned `analysis_manifest.json` describing the requested depth, effort and enabled capabilities for each building.

## Core principles

1. Deterministic checks and calculations remain deterministic whenever practical.
2. Operational source schemas are normalized through mappings into a stable canonical model.
3. Physical identity, site identity, transit/service-point identity, tenure and time remain distinct dimensions.
4. Every agent has bounded stage ownership.
5. Every transformation preserves source lineage.
6. Human review is captured as structured metadata inside the SPA.
7. Reviewer feedback can trigger revision but cannot silently overwrite authoritative source facts.
8. Reviewed and revised artifacts are versioned rather than overwritten.
9. Analysis depth is configurable without creating separate incompatible pipelines.
10. Building-level evidence and review controls remain separate from future portfolio optimization.
11. Model choice is task-dependent and recorded; methodology remains model-independent.
12. Current A/B/C/T/E contracts use required `building_id` and canonical `stage`; legacy `site_id-as-building` and `pipeline_state` conventions are deprecated.

## Repository layout

```text
.github/
  agents/
  prompts/

app/
  main.py
  cockpit.py

contracts/
profiles/
mappings/
crosswalks/
rules/

src/
  capabilities/
  context/
  costing/
  evaluation/
  orchestration/
  quality/
  review/
  selection/
  spa/
  validator/

spa_exchange/
  generated/
  under_review/
  reviewed/
  extracted/
  revised/
  archived/

examples/
tests/
docs/
```

## Versioned SPA lifecycle

```text
generated -> under_review -> reviewed -> extracted -> revised -> archived
```

Reviewed SPAs embed both the canonical site context and review metadata. The review extractor converts this into structured feedback for Agent R. Prior reviewed versions are preserved.

## Key documentation

- `docs/CANONICAL-CONVENTIONS.md` — normative current naming and architectural conventions.
- `docs/MASTERCLASS-COOKBOOK.md` — complete narrative learning and operating guide.
- `docs/COPILOT-WORK-ONBOARDING.md` — guided deployment and real-data onboarding protocol for GitHub Copilot.
- `docs/identity-and-occupancy-model.md` — transit/site/building/occupancy/mixed-tenure identity model.
- `docs/model-selection-guide.md` — task-based model routing and reminder strategy.
- `docs/information-model-v0.2.md` — detailed information model, refreshed to the current canonical view while retaining its historical filename.
- `docs/evolution-and-objectives.md` — why the solution evolved and what it is intended to do.
- `docs/pipeline-workflow.md` — Mermaid view of the end-to-end pipeline and revision loop.
- `docs/source-integration-architecture.md` — source-to-canonical mapping and integration approach.
- `docs/selection-hierarchy.md` — Region/Branch/Site/Building selection hierarchy and its distinction from occupancy relationships.
- `docs/v0.3-agent-a-live-test.md` — first live Copilot Agent A validation approach.
- `spa_exchange/README.md` — versioned SPA lifecycle and processing conventions.

## Production integration principle

Real operational data should remain outside source control. The repository should hold schemas, mapping templates, crosswalk definitions, business rules, agents, prompts, validation code, tests and synthetic fixtures. Local or approved enterprise data can feed the same canonical contracts without changing downstream agents.

## Future boundary

A downstream portfolio planning/optimization solution may consume approved building-level work packages to add portfolio scenarios, annual CAPEX constraints, project/delivery capacity, constrained scheduling and multi-year investment planning. Those capabilities are intentionally outside the current building-analysis product boundary.
