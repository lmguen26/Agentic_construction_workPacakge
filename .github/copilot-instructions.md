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

## Pipeline

1. Validator V: verify site source completeness and schema conformity.
2. Agent A: normalize deficiencies into opportunities.
3. Agent B: cluster opportunities and form candidate work packages using SALVO-inspired bundling and blending logic.
4. Agent C: apply or interpret deterministic cost indexation and indirect-cost outputs.
5. Agent T: formulate work recommendations and strategy.
6. Agent E: produce an executive synthesis from approved recommendations.
7. SPA generator: render structured outputs into a site building sheet.

## Artifact discipline

Each stage must:

- declare its expected input artifact;
- validate that the upstream stage is complete;
- produce only its declared output artifact;
- preserve IDs linking results to original records;
- include transformation metadata;
- stop when required information is missing.
