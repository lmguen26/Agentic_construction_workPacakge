# Agentic Construction Work Package

Synthetic reference architecture for a configurable, human-in-the-loop, site-centric investment-planning workflow. The solution transforms validated building information into normalized opportunities, clusters, work packages, costed work packages, recommendations, executive summaries, reviewable HTML SPAs, and structured revision feedback.

> Do not commit confidential operational data, production prompts, pricing tables, credentials, or real datasets to this public repository.

## Start here

**New to the methodology? Read [`docs/MASTERCLASS-COOKBOOK.md`](docs/MASTERCLASS-COOKBOOK.md) first.** It explains the business concepts, deterministic/agentic boundaries, every phase and agent, the cockpit, analysis levels, human review, revision loop, governance, common failure modes, and complete step-by-step operating recipes.

## Product objective

The repository is designed to support repeatable analysis of buildings **individually**, producing reviewed and traceable site-level work packages. It intentionally stops short of portfolio optimization. A future portfolio/scenario solution can consume approved work-package information products downstream.

The analysis is configurable: users can choose validation-only, baseline work-package analysis, strategic site analysis, advanced investment analysis, or a custom module combination. Every configured run is represented by an `analysis_manifest.json`.

## Core workflow

```text
Operational source data
        |
        v
Mappings / Crosswalks
        |
        v
Canonical Data Model
        |
        v
Deterministic Data Quality Gate
        |
        v
Canonical site_context.json
        |
        v
Configurable Analysis Manifest
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
[T] Site work recommendations / strategy
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
[R] Revision agent
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

## Desktop application

Run:

```bash
python app/main.py
```

The desktop application provides hierarchical multi-filter selection (`Region -> Branch -> Site -> Building`), multi-building batch scope, validation, site-context generation, HTML datasheet generation and access to the **Site Analysis Cockpit**. Batch operation preserves independent per-building artifacts and review histories.

The cockpit produces a versioned `analysis_manifest.json` describing the requested depth, effort and enabled capabilities.

## Core principles

1. Deterministic checks and calculations remain deterministic whenever practical.
2. Operational source schemas are normalized through mappings into a stable canonical model.
3. Every agent has bounded stage ownership.
4. Every transformation preserves source lineage.
5. Human review is captured as structured metadata inside the SPA.
6. Reviewer feedback can trigger revision but cannot silently overwrite authoritative source facts.
7. Reviewed and revised artifacts are versioned rather than overwritten.
8. Analysis depth is configurable without creating separate incompatible pipelines.
9. Site-level evidence and review controls remain separate from future portfolio optimization.

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

- `docs/MASTERCLASS-COOKBOOK.md` — complete narrative learning and operating guide; recommended starting point.
- `docs/evolution-and-objectives.md` — why the solution evolved and what it is intended to do.
- `docs/pipeline-workflow.md` — Mermaid view of the end-to-end pipeline and revision loop.
- `docs/source-integration-architecture.md` — source-to-canonical mapping and integration approach.
- `docs/selection-hierarchy.md` — Region/Branch/Site/Building selection hierarchy and its distinction from occupancy relationships.
- `docs/v0.3-agent-a-live-test.md` — first live Copilot Agent A validation approach.
- `spa_exchange/README.md` — versioned SPA lifecycle and processing conventions.

## Production integration principle

Real operational data should remain outside source control. The repository should hold schemas, mappings, crosswalk definitions, business rules, agents, prompts, validation code, tests and synthetic fixtures. Local or approved enterprise data can feed the same canonical contracts without changing downstream agents.

## Future boundary

A downstream portfolio planning/optimization solution may consume approved site-level work packages to add portfolio scenarios, annual CAPEX constraints, project/delivery capacity, constrained scheduling and multi-year investment planning. Those capabilities are intentionally outside the current site-centric product boundary.
