---
name: continue-pipeline-run
description: Execute only the currently requested specialist stage for one prepared building pipeline run.
agent: Work Package Orchestrator
argument-hint: run_dir=data/runs/BLDG-001/<analysis_id>
---

Continue exactly one stage of the prepared building pipeline run supplied as `run_dir`.

## Mandatory preparation

1. Read `docs/CANONICAL-CONVENTIONS.md`.
2. Read `<run_dir>/run_state.json`.
3. Read `<run_dir>/next_stage_request.json`.
4. Read `<run_dir>/analysis_manifest.json`.
5. Read `<run_dir>/site_context.json`.
6. Read the specialist agent named by `copilot_agent` in `next_stage_request.json`.
7. Read the declared contract in `contract_path`.
8. Read any prior artifact listed in `required_inputs`.

Do not choose a different stage. Do not skip ahead.

## Model reminder

Before executing, remind the user of the recommended model class for this task according to `docs/model-selection-guide.md`.

- A/B/T/E/R semantic reasoning: strongest suitable reasoning model; use Claude Opus when available for high-consequence or early validation runs.
- C arithmetic: deterministic Python is authoritative; use the agent only to consume/explain approved deterministic cost outputs.
- Independent challenge: use a different model family such as Gemini when available.

Do not permanently encode the selected vendor/model into the artifact contract. Record actual model metadata where supported.

## Execution

Execute only the requested specialist transformation.

- Use the canonical `building_id` from the run.
- Respect enabled modules in `analysis_manifest.json`.
- Preserve all source and upstream lineage.
- Do not compensate for missing or conflicting source data.
- Do not perform responsibilities owned by another stage.
- Return a JSON artifact conforming exactly to the declared contract.
- Write the JSON to the exact `output_path` under `<run_dir>`.

Do **not** invoke the next agent after writing the file.

## Controlled advancement

After the artifact has been written, run or instruct the user to run:

```bash
python scripts/run_pipeline.py advance <run_dir>
```

If validation passes, Python will create a new `next_stage_request.json` for the next enabled stage. If validation fails, correct the current-stage artifact only; do not bypass validation.

When the run reaches `READY_TO_PUBLISH`, generate the SPA with:

```bash
python scripts/run_pipeline.py publish <run_dir>
```

The SPA is the reviewer-facing artifact. Human review and Agent R occur only after publication/review metadata is available.
