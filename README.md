# Agentic Construction Work Package

Synthetic reference architecture for a human-in-the-loop workflow that transforms building-condition data into normalized opportunities, clusters, work packages, costed work packages, recommendations, summaries, and a site-level HTML building sheet.

> Do not commit employer-confidential data, production prompts, pricing tables, credentials, or real datasets to this public repository.

## Workflow

```text
Source data (Excel / JSON / CSV)
        |
        v
[V] Deterministic Site Validator
        |
        v
[A] Deficiency -> Opportunity normalization
        |
        v
[B] SALVO-inspired clustering / bundling / blending
        |
        v
[C] Cost indexation + indirect costs
        |
        v
[T] Work recommendations / strategy
        |
        v
[E] Executive synthesis
        |
        v
Structured site artifact -> HTML SPA building sheet
```

## Core principle

Every stage consumes a structured input artifact and produces a structured output artifact. LLM agents interpret bounded data; deterministic code performs validations and calculations that should not depend on model judgment.

## Repository layout

```text
.github/
  copilot-instructions.md
  agents/
    orchestrator.agent.md
    agent-a-opportunity.agent.md
    agent-b-workpackage.agent.md
    agent-c-cost.agent.md
    agent-t-strategy.agent.md
    agent-e-summary.agent.md
  prompts/
contracts/
rules/
src/
  validator/
  orchestration/
  spa/
examples/
tests/
```

## Pipeline states

`INGESTED -> VALIDATED -> OPPORTUNITIES -> CLUSTERED -> COSTED -> RECOMMENDED -> SUMMARIZED -> PUBLISHED`

Validation failure produces `BLOCKED`; downstream agents must not infer missing source data.

## VS Code / GitHub Copilot

The `.github/agents` files define specialized custom agents. The orchestrator coordinates the sequence and exposes handoffs to the next stage. `.github/prompts` can hold reusable entry-point tasks. Business rules should live under `/rules` rather than being buried only in prompts.

## Recommended production split

- Python / Excel / JSON: source validation, joins, schema validation, deterministic formulas, cost calculations, pipeline state.
- Copilot agents: normalization, bounded interpretation, clustering rationale, strategic recommendations, summaries.
- Human: review, exceptions, approval, release.

## Next implementation steps

1. Add sanitized JSON Schemas for every handoff.
2. Add the 8-9 source-presence rules to the deterministic validator.
3. Replace the synthetic agent instructions with sanitized versions of production prompts.
4. Add versioned quantitative business rules under `/rules`.
5. Connect the final structured artifact to the Python/Tkinter HTML SPA generator.
