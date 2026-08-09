---
description: Extract structured reviewer feedback from a reviewed building datasheet SPA and prepare a controlled revision cycle.
agent: Agent R Review Revision
---

Use the reviewed HTML building datasheet supplied by the user as a portable review package.

1. Extract the embedded `site-context` JSON block.
2. Extract the embedded `review-metadata` JSON block.
3. Do not scrape rendered HTML text when the embedded JSON contains the same information.
4. Convert the review metadata into a structured feedback payload conforming to `contracts/review-feedback.schema.json`.
5. Verify that `building_id`, `review_id`, reviewer identity, source artifact version, timestamps, and work-package IDs are present and consistent.
6. Classify feedback as `NO_REVISION_REQUIRED`, `REVISION_REQUIRED`, `PARTIAL_REVISION_REQUIRED`, or `HUMAN_ESCALATION_REQUIRED`.
7. Treat reviewer comments as revision instructions/evidence, not authoritative source facts.
8. If a reviewer comment contradicts the canonical site context, preserve the canonical fact and flag `requires_source_update` or `requires_human_escalation`.
9. Route cost-impacting changes back through deterministic costing rather than editing calculated costs directly.
10. Produce a new versioned revision candidate with a `revision_log`; never overwrite the prior artifact.
11. The revised candidate must return to human review before becoming final.
