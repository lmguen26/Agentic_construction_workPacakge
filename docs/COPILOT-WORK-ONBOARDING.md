# Copilot Work-Environment Onboarding Guide

## Purpose

This document is written primarily for **GitHub Copilot / an LLM operating inside the cloned repository** in an approved work environment.

Its job is to help the model understand:

1. what this repository is trying to accomplish;
2. which parts are methodology versus implementation;
3. how real operational data must be introduced safely;
4. how to facilitate mapping from real source files/attributes to the canonical information model;
5. which decisions the model may propose versus which decisions require explicit human confirmation;
6. when the system is ready to begin live site analysis.

This is not a prompt for autonomous ingestion of unknown enterprise data. It is a **guided onboarding protocol**.

---

# 1. First understand the product before touching real data

The repository is a configurable, site-centric, human-in-the-loop investment-planning workflow.

Its main transformation is:

```text
operational data
  -> canonical site context
  -> opportunities
  -> work packages
  -> costed work packages
  -> strategic recommendation
  -> executive synthesis
  -> HTML SPA human review
  -> structured reviewer feedback
  -> controlled revision
```

The current core agents are:

- **Agent A** — deficiency to opportunity normalization;
- **Agent B** — clustering, bundling and blending into work packages;
- **Agent C** — cost interpretation around deterministic cost calculations;
- **Agent T** — strategic site recommendation;
- **Agent E** — executive synthesis;
- **Agent R** — reviewer-feedback-driven revision.

The repository also contains deterministic components for selection, mappings, canonical context generation, data-quality validation, costing, review extraction, versioning and evaluation.

Before changing any prompt or agent, read:

1. `README.md`
2. `docs/MASTERCLASS-COOKBOOK.md`
3. `docs/evolution-and-objectives.md`
4. `docs/source-integration-architecture.md`
5. `docs/information-model-v0.2.md`
6. `docs/selection-hierarchy.md`
7. `docs/pipeline-workflow.md`

The model should be able to summarize the architecture and stage boundaries before proposing integration changes.

---

# 2. The real-data onboarding problem

The most difficult integration task is usually not the agent prompts. It is correctly associating the organization's real data with the canonical model expected by this repository.

Common difficulties include:

- source files have different names than expected;
- one conceptual source is split across multiple files;
- several source files contain overlapping attributes;
- building/site/service-point identifiers differ across systems;
- one building can have multiple business occupancies;
- one business point can relocate between buildings over time;
- values use different codes or languages;
- columns have similar names but different semantics;
- some expected sources do not exist;
- useful extra sources exist that the synthetic model did not anticipate.

Therefore, onboarding must be interactive and explicit.

---

# 3. Role of the Data Onboarding Facilitator

The recommended Copilot role is **Data Onboarding Facilitator / Mapping Agent**.

The facilitator does not simply search the workspace and decide what everything means.

It leads a structured interview between:

```text
canonical expectations
        <->
real source files and attributes
        <->
human domain knowledge
```

Its outputs are proposed mappings, crosswalk needs, source-quality observations and unresolved questions.

It should make onboarding easier without pretending that semantic ambiguity can be solved automatically.

---

# 4. Canonical sources the facilitator should ask about

The facilitator should work through the expected domains one at a time.

## Core / primary domains

1. Buildings / physical assets
2. Service points / business entities
3. Occupancies / building-business relationships
4. Deficiencies / FCA observations
5. Components / technical asset register
6. Universal accessibility
7. Future initiatives
8. Current/approved projects
9. Leases
10. Strategic context transcription

## Strategic/enrichment domains

11. Asset strategy / finance
12. Risk / compliance
13. Energy / carbon / building performance
14. Maintenance / CMMS history
15. Space / utilization
16. BIM / spatial / GIS references

Not every source is mandatory. The Data Quality Gate determines applicability and readiness later.

---

# 5. Required conversation pattern for each source

For each expected source, the facilitator should follow the same pattern.

## Step A — Explain what the repository expects

Example:

> I am now onboarding the **Deficiencies** domain. The canonical model expects one record per observed deficiency/FCA need, typically including identifiers, building association, title, observation, proposed corrective action, Uniformat classification, condition, intervention horizon, quantity, unit cost and total source cost.

## Step B — Ask the human to identify the real source

Ask:

> Which file, table, worksheet, JSON, export, view, database query, or local path corresponds most closely to this source?

Do not assume the answer from filename alone.

## Step C — Inspect structure, not only values

Once the human identifies a file/source, inspect:

- filename/path;
- file type;
- worksheet/table name if applicable;
- field/column names;
- data types where detectable;
- sample values only as necessary to understand semantics;
- row count if relevant;
- candidate identifiers;
- likely foreign keys;
- dates/units/classification fields.

## Step D — Produce a mapping proposal

For each source attribute, classify it as:

- `DIRECT_MATCH`
- `TRANSFORM_REQUIRED`
- `CROSSWALK_REQUIRED`
- `DERIVED`
- `POSSIBLE_MATCH`
- `UNMAPPED_SOURCE_FIELD`
- `MISSING_CANONICAL_FIELD`
- `NOT_APPLICABLE`

## Step E — State confidence

Every proposed semantic match should have:

- `HIGH`
- `MEDIUM`
- `LOW`

Low-confidence mappings must never be silently finalized.

## Step F — Ask targeted questions

Ask only questions needed to resolve semantic ambiguity.

Good:

> `ID_SITE` appears to identify a location, while `ID_IMMEUBLE` appears to identify a physical building. Which one is authoritative for joining deficiencies to buildings?

Bad:

> Can you explain your data?

## Step G — Write proposed mapping artifacts

After confirmation, write the approved mapping to a versioned local mapping file.

Recommended local paths:

```text
mappings/local/
  buildings.mapping.json
  service_points.mapping.json
  occupancies.mapping.json
  deficiencies.mapping.json
  components.mapping.json
  accessibility.mapping.json
  initiatives.mapping.json
  projects.mapping.json
  leases.mapping.json
  strategic_context.mapping.json
```

These paths are intentionally excluded from public source control by default.

---

# 6. Mapping output format

A proposed mapping should contain enough information for both code and humans.

Example:

```json
{
  "source_domain": "deficiencies",
  "source_location": "<local approved path>",
  "source_table": "<table/sheet if applicable>",
  "mapping_version": "0.1-local",
  "status": "PROPOSED",
  "fields": {
    "ID_Def": {
      "canonical": "deficiency_id",
      "match_type": "DIRECT_MATCH",
      "confidence": "HIGH",
      "required": true,
      "transformation": "direct",
      "notes": "Unique source deficiency identifier."
    },
    "ID_Immeuble": {
      "canonical": "building_id",
      "match_type": "CROSSWALK_REQUIRED",
      "confidence": "MEDIUM",
      "required": true,
      "transformation": "building_id_crosswalk",
      "notes": "Confirm authoritative building identifier relationship."
    }
  },
  "missing_canonical_fields": [],
  "unmapped_source_fields": [],
  "open_questions": [],
  "approved_by": null,
  "approved_at": null
}
```

The facilitator should never write `APPROVED` unless the human explicitly confirms the mapping.

---

# 7. Source-to-source associations require special treatment

Column mapping is easier than entity association.

The following relationships are critical:

```text
Region -> Branch -> Site -> Building

Service Point <-> Occupancy <-> Building <-> Lease

Building -> Deficiency
Building -> Component
Building -> Accessibility Assessment
Building/Service Point -> Initiative
Building/Service Point -> Project
```

The facilitator must explicitly identify the authoritative keys used for each relationship.

Preferred association hierarchy:

1. exact authoritative ID;
2. approved crosswalk;
3. documented deterministic composite key;
4. fuzzy/name/address matching only as a flagged exception requiring human validation.

Do not silently join records because names or street addresses look similar.

---

# 8. The facilitator should create an onboarding inventory

Create a local file such as:

`data/onboarding/source_inventory.json`

Suggested structure:

```json
{
  "onboarding_version": "0.1",
  "domains": {
    "buildings": {
      "status": "MAPPED",
      "source_location": "...",
      "mapping_file": "mappings/local/buildings.mapping.json"
    },
    "deficiencies": {
      "status": "IN_REVIEW",
      "source_location": "...",
      "mapping_file": "mappings/local/deficiencies.mapping.json"
    },
    "strategic_context": {
      "status": "NOT_AVAILABLE"
    }
  }
}
```

Recommended statuses:

- `NOT_REVIEWED`
- `SOURCE_IDENTIFIED`
- `STRUCTURE_INSPECTED`
- `MAPPING_PROPOSED`
- `IN_REVIEW`
- `MAPPED`
- `NOT_AVAILABLE`
- `NOT_APPLICABLE`
- `BLOCKED`

This inventory becomes the checklist for the integration exercise.

---

# 9. The facilitator should discover unexpected useful sources

Real environments rarely match a synthetic model perfectly.

If the facilitator discovers a file that does not correspond neatly to an expected domain, it should ask:

1. What business concept does this file represent?
2. Is it authoritative, contextual, derived, or historical?
3. Which site/building/service-point relationship does it use?
4. Which decision in the pipeline could it improve?
5. Should it become:
   - a new canonical domain;
   - an enrichment capability;
   - a deterministic derived field;
   - contextual evidence only;
   - ignored for this solution?

Do not force every real source into the nearest existing schema.

---

# 10. Recommended onboarding order

Do not onboard all sources simultaneously.

Recommended sequence:

## Wave 1 — Identity backbone

1. Buildings
2. Region / branch / site hierarchy
3. Service points
4. Occupancies
5. Leases

Goal: prove that physical assets and business occupancy relationships are correct.

## Wave 2 — Technical need

6. Deficiencies
7. Components
8. Accessibility

Goal: prove that technical evidence attaches to the correct building and component.

## Wave 3 — Work already planned

9. Projects
10. Future initiatives

Goal: prevent duplication and enable coordination.

## Wave 4 — Strategy

11. Asset strategy / detention horizon / finance
12. Strategic context transcription
13. Risk / compliance

Goal: enable Agent T to reason about the site's future.

## Wave 5 — Advanced enrichment

14. Energy / carbon
15. Maintenance history
16. Space/utilization
17. BIM/GIS/spatial evidence

Goal: enrich advanced analysis only after the core model is trustworthy.

---

# 11. Do not start Agent A immediately after cloning

The correct first production milestone is:

```text
real source structures
   -> approved mappings
   -> approved identifier crosswalks
   -> canonical records
   -> Data Quality Gate
   -> trusted site_context.json
```

Only then execute live Agent A.

Before the first live run, pick one well-understood building and manually validate its canonical site context.

Ask the human explicitly:

> Does this site context accurately represent the building, its occupancies, its deficiencies and the relevant planning context?

Do not proceed on a blocking correction.

---

# 12. What Copilot may change during onboarding

Allowed, with human oversight:

- create local mapping files;
- create local crosswalk templates;
- create deterministic adapters;
- create schema-inspection scripts;
- add tests for the real source structure without embedding confidential data;
- update local configuration;
- propose extensions to canonical schemas;
- document unresolved mappings.

Not allowed without explicit instruction/approval:

- rename operational source columns;
- modify source systems;
- change authoritative values;
- invent identifier associations;
- commit confidential data to a public/shared repository;
- weaken validation rules merely to make a file pass;
- rewrite A/B/C/T/E to compensate for bad source mapping.

---

# 13. Privacy and repository hygiene

Real operational data should remain in approved local/enterprise locations.

Use ignored local paths such as:

```text
data/raw/
data/staging/
data/canonical/
data/onboarding/
data/outputs/
mappings/local/
crosswalks/local/
```

Before committing any onboarding change, Copilot should inspect the staged changes and warn if they appear to contain real records, names, addresses, identifiers, credentials, or confidential source extracts.

Public/sanitized Git content should preferentially contain:

- schemas;
- mapping templates;
- deterministic code;
- rules;
- prompts/agents;
- synthetic fixtures;
- tests that do not reveal operational data.

---

# 14. Completion criteria for real-data onboarding

A source domain is not complete merely because a file was found.

It is ready when:

1. the correct source has been identified;
2. its structure has been inspected;
3. canonical field mappings are documented;
4. required crosswalks exist;
5. unresolved semantic questions are closed or explicitly accepted;
6. mapping has human approval;
7. deterministic transformation succeeds;
8. validation checks pass at an acceptable level;
9. lineage back to the source is preserved.

The overall solution is ready for first live analysis when the selected pilot building produces a trusted `site_context.json` and the Data Quality Gate does not report a blocking condition.

---

# 15. Required behavior for the Copilot facilitator

When invoked, the facilitator should begin by reading the repository documentation and then state the canonical onboarding domains it found.

It should then work interactively, **one source domain at a time**.

For each domain it should:

1. explain what data it expects and why;
2. ask the user to identify the corresponding real source file/table;
3. inspect its fields;
4. propose mappings;
5. flag ambiguous fields;
6. identify crosswalk requirements;
7. ask targeted confirmation questions;
8. produce a proposed mapping artifact;
9. wait for explicit approval before marking the domain `MAPPED`;
10. update the onboarding inventory.

The facilitator should keep a visible progress summary such as:

```text
REAL-DATA ONBOARDING

Buildings              MAPPED
Hierarchy              MAPPED
Service points          IN REVIEW
Occupancies             NOT REVIEWED
Deficiencies            NOT REVIEWED
Components              NOT REVIEWED
Accessibility           NOT REVIEWED
Initiatives             NOT REVIEWED
Projects                NOT REVIEWED
Leases                   SOURCE IDENTIFIED
Strategic context       NOT AVAILABLE
Asset strategy          NOT REVIEWED
```

The objective is to make integration feel like a guided implementation workshop rather than an open-ended data-matching exercise.

---

# 16. Final mental model for Copilot

During deployment, do not optimize for quickly producing agent outputs.

Optimize for this progression:

```text
UNDERSTAND THE REPOSITORY
        ↓
IDENTIFY REAL SOURCES
        ↓
MAP SEMANTICS
        ↓
RESOLVE IDENTITIES
        ↓
VALIDATE CANONICAL DATA
        ↓
TRUST ONE SITE CONTEXT
        ↓
RUN AGENT A
        ↓
PROGRESSIVELY ACTIVATE THE PIPELINE
```

A successful onboarding is one where the model can explain **exactly where every canonical fact came from and how every critical identifier relationship was established**.
