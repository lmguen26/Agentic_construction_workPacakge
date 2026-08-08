---
description: Prepare and review the deterministic canonical site context before Agent A.
agent: Work Package Orchestrator
---

Prepare the selected building for the agentic work-package pipeline.

1. Run or inspect the deterministic Site Context Builder output.
2. Confirm the `site_context.json` conforms to `contracts/site-context.schema.json`.
3. Confirm `data_quality.status` is not `BLOCKED`.
4. Review association exceptions and multi-occupant warnings.
5. Confirm `detention_horizon_years` and `detention_band` use the canonical detention terminology.
6. Do not infer missing source facts.
7. If the context is valid, hand off to Agent A Opportunity Normalizer.

The site context, not the raw portfolio tables, is the canonical input to Agent A.