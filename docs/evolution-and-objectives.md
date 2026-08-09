# Solution Evolution and Objectives

## Purpose
This repository is a **site-centric investment-planning and work-package production engine**. Its primary purpose is to process buildings individually, transform validated evidence into traceable work packages, support human review, and preserve the lineage of decisions and revisions.

It is intentionally not a portfolio optimization engine. Portfolio aggregation, scenario optimization and multi-year program balancing should consume approved site-level information products through a separate downstream solution when required.

## Evolution

### Stage 1 — Deterministic source validation
The solution began with a deterministic validator that confirms whether the required source domains exist for a selected building and whether their key relationships are coherent.

Objective: prevent agent reasoning on missing or mis-associated data.

### Stage 2 — Fixed agentic work-package pipeline
A bounded A-B-C-T-E sequence was introduced:

- **Agent A** — normalize deficiencies into opportunities.
- **Agent B** — cluster, bundle and blend opportunities into candidate work packages using SALVO-inspired concepts.
- **Agent C** — apply/interpret deterministic cost indexation and indirect-cost logic.
- **Agent T** — formulate site-level work recommendations.
- **Agent E** — summarize approved recommendations without changing work-package structure.

Objective: separate responsibilities, preserve lineage and avoid one unrestricted agent performing all transformations.

### Stage 3 — Canonical information model
Operational source schemas were separated from a stable canonical model through mappings and crosswalks.

Objective: allow source systems and column names to change without forcing prompt, contract or downstream-agent changes.

### Stage 4 — Canonical site context
A deterministic `site_context.json` was introduced as the authorized per-building information product consumed by the agents.

Objective: assemble only the relevant building, service-point, occupancy, lease, deficiency, component, accessibility, initiative, project, strategy and contextual evidence before agent execution.

### Stage 5 — Data Quality Gate
Source availability evolved from simple presence/absence into explicit quality states such as `COMPLETE`, `PARTIAL`, `CONFLICT`, `STALE`, `NOT_APPLICABLE` and `MISSING`, with blocking/warning/informational severity.

Objective: distinguish genuinely blocking problems from acceptable missing or non-applicable information.

### Stage 6 — Human-in-the-loop HTML SPA
The building datasheet evolved from a static output into the sole reviewer interface. It now embeds canonical site context and machine-readable review metadata.

Objective: give reviewers one practical interface while preserving structured reviewer identity, timestamps, decisions, comments, completion confirmation and audit events.

### Stage 7 — Review and revision loop
Reviewed SPAs became portable review packages. Structured review feedback can be extracted and supplied to **Agent R**, which produces a revision while preserving prior versions and authoritative source facts.

Objective: support iterative human-agent refinement without overwriting history.

### Stage 8 — Versioned SPA lifecycle
A dedicated `spa_exchange/` lifecycle was added:

`generated -> under_review -> reviewed -> extracted -> revised -> archived`

Objective: make each review/revision round explicit and auditable.

### Stage 9 — Configurable analysis depth
The solution now supports an **Analysis Cockpit** and `analysis_manifest.json` so a user can choose how much of the site-analysis capability is applied.

Objective: avoid applying maximum analytical complexity to every building while maintaining a common governed pipeline.

## Analysis profiles

### Level 0 — Validation only
Runs deterministic validation and canonical site-context generation without creating work packages.

Use when the immediate need is data inspection, readiness checking or source correction.

### Level 1 — Work Package Analysis
Runs the core A-B-C-T-E sequence and produces a reviewable building information product.

This is the standard baseline for site-by-site work-package production.

### Level 2 — Strategic Site Analysis
Adds strategic enrichment such as detention horizon, lease/occupancy constraints, future initiatives, existing projects, accessibility, component lifecycle, FCI/replacement-value context, risk/compliance and structured strategic context where available.

Use when recommendations need to account for broader site strategy rather than technical deficiencies alone.

### Level 3 — Advanced Investment Analysis
Adds advanced modules such as cost sensitivity/uncertainty, amortization, alternative work-package configurations and timing alternatives.

Use for high-value, complex or strategically important buildings.

### Custom
Allows experienced users to enable or disable individual capabilities. The resulting selections are recorded in the analysis manifest.

## Analysis effort
Analysis depth and analysis effort are intentionally separate controls.

- **RAPID** — reduced analytical breadth; focus on material issues and obvious coordination opportunities.
- **STANDARD** — normal site-level processing and review depth.
- **THOROUGH** — expanded alternatives, conflict checks, uncertainty treatment and review depth for complex/high-value sites.

Effort must have explicit execution meaning. It must never be interpreted as an instruction for an LLM to simply “think harder.”

## Analysis Manifest
Every configured run should produce an `analysis_manifest.json` containing:

- building ID;
- analysis profile;
- effort;
- selected capabilities;
- module applicability/readiness;
- requester;
- timestamp;
- pipeline version;
- rule versions.

The manifest becomes part of the provenance of the resulting SPA and downstream review cycle.

## Design principles

1. **Deterministic before probabilistic** — validation, calculations, identifier joins and source transformations remain deterministic whenever practical.
2. **Canonical downstream contracts** — agents consume canonical information, not source-system-specific schemas.
3. **Bounded agent ownership** — every agent has a defined transformation responsibility.
4. **Human decisions are structured data** — reviewer input is captured as machine-readable metadata, not only free text.
5. **No silent source correction** — reviewer or agent statements that conflict with authoritative facts are escalated back to source correction/validation.
6. **Version rather than overwrite** — reviewed and revised SPAs and work-package artifacts retain prior versions.
7. **Analysis depth is configurable** — buildings can receive different levels of analytical treatment while using one governed architecture.
8. **Site first, portfolio later** — this repository produces trusted site-level information products; portfolio optimization remains a downstream concern.

## Current objective
The current product objective is to support repeatable analysis of a finite set of buildings individually, producing reviewed and traceable site-level work packages with enough metadata to support later consolidation into broader investment planning.

## Future boundary
A future portfolio planning/optimization solution may consume approved work-package artifacts and add:

- annual CAPEX constraints;
- project-count/delivery-capacity constraints;
- portfolio scenarios;
- prioritization across sites;
- constrained scheduling;
- portfolio-level risk/condition outcomes;
- multi-year investment plans.

Those capabilities should not be allowed to weaken the site-level evidence, review and lineage controls established here.
