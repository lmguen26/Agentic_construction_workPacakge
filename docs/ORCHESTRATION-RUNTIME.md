# Orchestration Runtime — Python Control Plane + GitHub Copilot Agent Execution

## Purpose

This document defines how the configurable Site Analysis Cockpit becomes an executable building-level pipeline without coupling the methodology to a private LLM API.

The governing split is:

```text
Python = control plane
Copilot agents = bounded semantic transformations
HTML SPA = human review surface
```

Python owns sequence, state, contracts, file paths, validation, deterministic calculations, run history and publication. Copilot owns only the requested semantic stage.

## Why this design

GitHub Copilot in VS Code is the intended work-environment interaction surface. The Python desktop application should not pretend it can directly invoke a selected Copilot model unless an approved programmatic interface exists.

Instead, the orchestrator creates a structured request that Copilot can execute from the same repository workspace.

This avoids:

- embedding external API keys;
- bypassing enterprise Copilot controls;
- creating a second prompt-management system;
- letting an LLM decide pipeline sequence;
- allowing one agent to silently jump across stage boundaries.

## One run = one building

A batch selection may prepare many runs, but every run remains independent:

```text
Batch: 12 selected buildings
   |
   +-> RUN-BLDG-001
   +-> RUN-BLDG-002
   +-> RUN-BLDG-003
   ...
```

Each run receives its own manifest, site context, stage artifacts, validation history and SPA.

## Run folder

Prepared runs are stored under ignored local data paths:

```text
data/runs/
  <building_id>/
    <analysis_id>/
      analysis_manifest.json
      site_context.json
      data_quality_gate.json
      run_state.json
      next_stage_request.json
      artifacts/
        opportunities.json
        work_packages.json
        costed_work_packages.json
        recommendations.json
        building_summary.json
```

Real run folders remain outside Git because `data/` is ignored.

## Run states

Typical states are:

```text
PREPARED
WAITING_FOR_AGENT
STAGE_VALIDATION_FAILED
READY_TO_PUBLISH
SPA_GENERATED
COMPLETED
BLOCKED
CONFIGURATION_INVALID
```

`BLOCKED` is driven by the deterministic Data Quality Gate.

`CONFIGURATION_INVALID` protects against impossible custom-stage combinations, for example enabling Agent T while disabling the required upstream C stage.

## Stage sequence

The controlled baseline chain is:

```text
A OPPORTUNITIES
  -> B CLUSTERED
      -> C COSTED
          -> T RECOMMENDED
              -> E SUMMARIZED
```

Custom profiles may stop earlier, but downstream stages cannot bypass their required upstream stage.

## Preparing a run from the cockpit

1. Open `python app/main.py`.
2. Open **Site Analysis Cockpit**.
3. Select Region / Branch / Site / Building scope.
4. Choose analysis profile and effort.
5. Confirm capabilities.
6. Click **Prepare Copilot pipeline run(s)**.

For each non-blocked building, Python:

1. creates an `analysis_manifest.json`;
2. runs the Data Quality Gate;
3. builds canonical `site_context.json`;
4. validates stage dependencies;
5. creates `run_state.json`;
6. creates exactly one `next_stage_request.json` for the first enabled stage.

## Using GitHub Copilot

In VS Code Copilot Chat use:

```text
/continue-pipeline-run run_dir=data/runs/<building>/<analysis_id>
```

The prompt instructs Copilot to read:

- canonical conventions;
- run state;
- next-stage request;
- analysis manifest;
- site context;
- declared specialist agent;
- declared JSON contract;
- previous upstream artifact when applicable.

Copilot then writes **only one stage artifact**.

It does not invoke the next agent.

## Advancing the run

After Copilot writes the artifact:

```bash
python scripts/run_pipeline.py advance data/runs/<building>/<analysis_id>
```

Python validates:

- expected stage;
- required `building_id`;
- exact JSON Schema for the stage;
- building identity consistency.

If validation fails:

```text
status = STAGE_VALIDATION_FAILED
```

The current artifact must be corrected. The next stage is not exposed.

If validation passes, Python records PASS and replaces `next_stage_request.json` with the next valid stage request.

## Contract validation

Full runtime schema validation uses `jsonschema`.

Install dependencies after cloning:

```bash
python -m pip install -r requirements.txt
```

The important principle is that Copilot output is never trusted merely because it is valid-looking JSON.

## Model reminders

`next_stage_request.json` contains a model-selection hint.

Current default:

```text
A/B/T/E: strong structured reasoning model
        Claude Opus preferred for high-consequence/early validation

C: deterministic Python controls arithmetic

Independent challenge: another model family such as Gemini
```

The methodology remains model-agnostic.

## Deterministic reference mode

For development, the cockpit includes **Run deterministic reference pipeline**.

This exercises:

- run creation;
- stage sequencing;
- JSON contracts;
- state progression;
- SPA publication.

It uses synthetic deterministic reference fixtures instead of live LLM reasoning.

It must never be interpreted as a production recommendation.

CLI equivalent:

```bash
python scripts/run_pipeline.py reference data/outputs/BLDG-001.analysis_manifest.json
```

## Publishing the SPA

When all enabled stages have passed validation:

```text
status = READY_TO_PUBLISH
```

Generate the reviewer SPA:

```bash
python scripts/run_pipeline.py publish data/runs/<building>/<analysis_id>
```

The SPA is placed in:

```text
spa_exchange/generated/
```

The orchestrator merges:

- canonical site context;
- opportunities;
- work packages;
- costed work packages;
- T recommendations;
- E summary;

and creates a reviewer-facing `recommended_work_packages` view while preserving the underlying stage artifacts.

## Human review remains downstream

After publication:

```text
Generated SPA
   -> reviewer
   -> embedded review metadata
   -> reviewed SPA
   -> feedback extractor
   -> Agent R
   -> revised version
```

The orchestrator does not treat generated recommendations as final approval.

## Level 0 behavior

A Level 0 manifest enables no A/B/C/T/E stages.

The run therefore moves from deterministic validation/context directly to:

```text
READY_TO_PUBLISH
```

The resulting SPA is a validated building datasheet rather than a recommended-work-package review package.

## Live-data deployment sequence

When the repository is cloned into the approved work environment:

```text
Agent M onboarding
  -> approved mappings/crosswalks
  -> one trusted real site_context.json
  -> Data Quality Gate accepted
  -> Analysis Cockpit
  -> Prepare Copilot run
  -> /continue-pipeline-run
  -> advance
  -> repeat stage-by-stage
  -> publish SPA
  -> human review
```

Do not begin by automating all ~80 buildings. Establish one trusted pilot building, validate live Agent A, then progressively activate B, C, T and E before scaling batch throughput.

## Commands quick reference

Install:

```bash
python -m pip install -r requirements.txt
```

Desktop app:

```bash
python app/main.py
```

Prepare from a saved manifest:

```bash
python scripts/run_pipeline.py prepare data/outputs/BLDG-001.analysis_manifest.json
```

Advance after one Copilot stage:

```bash
python scripts/run_pipeline.py advance data/runs/BLDG-001/<analysis_id>
```

Publish:

```bash
python scripts/run_pipeline.py publish data/runs/BLDG-001/<analysis_id>
```

Reference-mode test:

```bash
python scripts/run_pipeline.py reference data/outputs/BLDG-001.analysis_manifest.json
```

Tests:

```bash
python -m pytest -q
```

## Governing rule

**The LLM proposes the bounded transformation. Python controls whether the pipeline is allowed to proceed.**
