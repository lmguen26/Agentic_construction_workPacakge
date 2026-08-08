---
description: Start the site-level work-package workflow from a validated site artifact.
agent: Work Package Orchestrator
---

Run the construction work-package workflow for the selected site.

Requirements:

1. Identify the current pipeline state from the available site artifact.
2. If the site is not `VALIDATED`, stop and report the blocking validation issues.
3. If it is `VALIDATED`, prepare the handoff to Agent A.
4. At every stage, preserve site ID, source IDs, lineage, rule versions, assumptions, and exceptions.
5. Do not skip stages.
6. Do not infer missing source data.
7. Require explicit human review before progressing past any stage containing blocking exceptions.
8. End only when the structured artifact is `SUMMARIZED` and ready for deterministic SPA publication.
