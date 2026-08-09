# Repository Copilot Instructions

This repository models an auditable, human-in-the-loop construction work-package pipeline.

## Global rules

- Never fabricate missing source data.
- Treat deterministic validation failures as blocking.
- Preserve source identifiers and lineage through every stage.
- Prefer structured JSON artifacts over free-form prose between stages.
- Do not silently modify upstream facts.
- Separate deterministic calculations from LLM interpretation.
- Record assumptions, exceptions, and confidence where applicable.
- Business rules belong in `/rules` and must be referenced by version.
- Final recommendations require human review before publication.

## Model-selection reminder

Before a major task, identify the task type and remind the user which model class is preferred. Read `docs/model-selection-guide.md`.

Default guidance when those models are available in the current GitHub Copilot environment:

- **Claude Opus / strongest reasoning model:** repository comprehension, Agent M real-data onboarding, semantic source mapping, identity/occupancy ambiguity, architecture review, early Agent B/T validation.
- **Codex / strongest coding model:** Python adapters, validators, schemas, tests, orchestration, refactoring and debugging after semantic decisions are explicit.
- **Gemini / different model family:** independent challenge, second opinion, large-context cross-check and adversarial review of recommendations produced by another model family.
- **Deterministic Python:** authoritative calculations and validations whenever practical, especially Agent C cost arithmetic.

Do not permanently bind an agent role to a vendor/model. Model names and availability change. Keep contracts, rules and evaluators model-agnostic and record the actual model used in run metadata.

For high-consequence semantic tasks, explicitly surface a short reminder such as:

> Model recommendation: use the strongest available reasoning model (currently Claude Opus if available) before continuing this onboarding/architecture task.

For implementation tasks, surface:

> Model recommendation: switch to the strongest available coding model (currently Codex if available) for implementation and tests.

For independent evaluation, surface:

> Model recommendation: use a different model family (for example Gemini if available) to challenge the generated artifact, while deterministic evaluators remain authoritative.

## Pipeline

1. Validator V: verify site source completeness and schema conformity.
2. Agent A: normalize deficiencies into opportunities.
3. Agent B: cluster opportunities and form candidate work packages using SALVO-inspired bundling and blending logic.
4. Agent C: apply or interpret deterministic cost indexation and indirect-cost outputs.
5. Agent T: formulate work recommendations and strategy.
6. Agent E: produce an executive synthesis from approved recommendations.
7. SPA generator: render structured outputs into a site building sheet.
8. Human review: capture reviewer decisions and metadata in the SPA.
9. Agent R: process structured reviewer feedback into controlled revisions.

## Artifact discipline

Each stage must:

- declare its expected input artifact;
- validate that the upstream stage is complete;
- produce only its declared output artifact;
- preserve IDs linking results to original records;
- include transformation metadata;
- stop when required information is missing.
