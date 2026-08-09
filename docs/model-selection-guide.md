# Task-Based LLM Selection Guide

## Purpose

This repository is intentionally **model-agnostic**. The methodology, contracts, business rules, evaluators and deterministic controls must remain stable even when the available GitHub Copilot models change.

However, different tasks benefit from different model characteristics. This guide provides a practical default routing strategy.

## Default routing strategy

### 1. Architecture comprehension and real-data semantic onboarding

**Preferred model class:** strongest available reasoning / long-context model.

**Current preferred example when available:** Claude Opus.

Use for:
- first-time repository comprehension;
- Agent M real-data onboarding;
- difficult source-to-canonical semantic mapping;
- resolving transit/site/building/occupancy/lease conceptual ambiguity;
- architecture review across prompts, schemas, rules and documentation;
- strategic interpretation when ambiguity is expensive.

Why: these tasks are infrequent but high-consequence. A wrong semantic mapping can contaminate every downstream site analysis.

### 2. Coding, adapters, validators, tests and refactoring

**Preferred model class:** strongest available coding/repository model.

**Current preferred example when available:** Codex.

Use for:
- Python adapters;
- deterministic mapping/transformation code;
- Data Quality Gate implementation;
- JSON Schema work;
- tests and regression harnesses;
- orchestration code;
- refactoring;
- debugging.

Why: once the semantic decision is made, implementation should be concrete, testable and repository-aware.

### 3. Agentic site analysis

**Preferred model class:** strong structured reasoning model.

**Initial preferred example when available:** Claude Opus for early validation of A/B/T/E, especially B and T.

Use for:
- Agent A normalization when first validating behavior;
- Agent B clustering/bundling/blending;
- Agent T strategic recommendations;
- Agent E synthesis;
- Agent R review-driven revision.

Agent C calculations should remain deterministic wherever possible; the model should explain assumptions rather than invent authoritative arithmetic.

Once evaluators show stable behavior, faster/lower-cost models may be tested for routine runs.

### 4. Independent challenge / second opinion

**Preferred model class:** a different model family from the model that produced the artifact.

**Current useful example when available:** Gemini.

Use for:
- adversarial review of work-package recommendations;
- checking unsupported assumptions;
- challenging lineage or semantic interpretation;
- comparing model behavior against the same evaluation invariants;
- reviewing large collections of artifacts as an independent perspective.

Avoid relying exclusively on the same model family for both generation and evaluation when a meaningful independent challenge is available.

## Practical default matrix

| Task | Preferred current example | Secondary use |
|---|---|---|
| Repository comprehension | Claude Opus | Gemini cross-check |
| Agent M onboarding | Claude Opus | Gemini challenge |
| Complex semantic mapping | Claude Opus | Independent review |
| Python implementation | Codex | Claude architecture check |
| Debugging/refactoring | Codex | — |
| Agent A early validation | Claude Opus | compare alternatives |
| Agent B | Claude Opus | Gemini challenge |
| Agent C arithmetic | Deterministic Python | LLM explanation only |
| Agent T | Claude Opus | Gemini challenge |
| Agent E | Claude / capable reasoning model | lower-cost model after validation |
| Agent R | Claude / capable reasoning model | independent review if material |
| Evaluation/challenge | Different model family | deterministic evaluator remains authoritative |

## Model choice is not methodology

Do not encode business logic that depends on a specific vendor/model.

Prefer:

```text
agent_role = "work_package_builder"
model_selection = configurable
contract = stable
rules = stable
evaluator = stable
```

not:

```text
Agent B = permanently Claude Opus
```

Model availability, names and performance will change. The repo should record which model was used for a run, but the methodology should remain portable.

## High-consequence rule

Use the strongest available reasoning model when **semantic ambiguity is expensive**, especially during:
- identity backbone onboarding;
- transit/site/building/occupancy reconciliation;
- mixed-tenure interpretation;
- first live Agent B/T validation;
- architecture changes affecting contracts or lineage.

Use coding-specialized models after the semantic decision is explicit.

## Reminder before starting a major task

Before executing a high-impact task, ask:

1. Is this primarily semantic/architectural reasoning?
2. Is this primarily coding/implementation?
3. Is this an independent evaluation/challenge?
4. Is deterministic code more appropriate than any LLM?

Then select the model accordingly.

## Recording model use

Where practical, run metadata should capture:

```json
{
  "agent": "B",
  "model_provider": "<provider>",
  "model_name": "<selected model>",
  "model_selected_for": "structured work-package reasoning",
  "prompt_version": "...",
  "rule_version": "..."
}
```

This supports later comparison across models without changing the underlying method.