---
name: run-agent-a-live
description: Run Agent A only against one canonical synthetic site context and save a contract-shaped opportunity artifact.
agent: Agent A Opportunity Normalizer
argument-hint: building_id=BLDG-A1
---

Run Agent A only. Do not invoke Agent B.

Use the requested synthetic archetype from `examples/archetypes/archetypes.json` and the deterministic context logic in `src/context/site_context_builder.py`.

For the requested `building_id`:
1. Build or inspect its canonical site context.
2. Stop if the data-quality gate is `BLOCKED`.
3. Normalize each deficiency into an opportunity according to `.github/agents/agent-a-opportunity.agent.md`.
4. Return JSON only, conforming exactly to `contracts/opportunities.schema.json`.
5. Preserve all source deficiency IDs and source facts.
6. Do not create clusters, work packages, cost indexation, or strategic recommendations.
7. Save/copy the resulting JSON to `examples/archetypes/live_agent_a/<building_id>.opportunities.json` when file-edit tools are available; otherwise output the complete JSON so it can be pasted there.

After generation, run the Agent A evaluator against the produced artifact and report PASS/FAIL with the failed invariant names.