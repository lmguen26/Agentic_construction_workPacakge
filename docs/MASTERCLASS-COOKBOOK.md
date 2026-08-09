# Masterclass & Cookbook — From Building Data to Reviewed Work Packages

## Who this guide is for

This guide is written for someone who understands buildings, projects, planning, maintenance, finance, data, or business operations but **does not need to be a software developer or AI specialist**.

It explains the solution as both:

- a **masterclass**: why the concepts exist, what problem each concept solves, and how the pieces fit together;
- a **cookbook**: what to do, in what order, what to inspect, what output to expect, and when to stop and ask for human judgment.

The solution is site-centric. It can select many buildings at once for operational efficiency, but every building remains an independent analysis unit with its own facts, work packages, review record, versions, and audit trail.

---

# Part I — The idea in plain language

## 1. What problem are we solving?

A building rarely has one clean source telling us exactly what investment should occur.

Instead, information is fragmented across building records, deficiencies, components, accessibility assessments, leases, business occupancies, future initiatives, current projects, strategy, risk, and sometimes a structured transcription of strategic context.

A human planner normally has to assemble this evidence mentally and answer several different questions:

1. Do I trust the information enough to start?
2. What actual needs are hidden in the raw deficiencies?
3. Which needs belong together?
4. What would the combined work cost?
5. Given the building's future, should the work actually proceed as proposed?
6. How do I explain the recommendation clearly?
7. Who reviewed it, what did they change, and what happens next?

This repository turns those questions into explicit phases.

```text
raw evidence
   -> trusted site context
   -> opportunities
   -> clusters and work packages
   -> costed work packages
   -> strategic recommendations
   -> executive synthesis
   -> reviewable building datasheet
   -> human review
   -> controlled revision
```

The goal is **not to remove professional judgment**. The goal is to give professional judgment a repeatable, traceable structure.

---

# Part II — Five concepts to understand before touching the application

## 2. Deterministic logic versus agent reasoning

This distinction is fundamental.

A deterministic function should produce the same result from the same inputs. Examples:

- validating that a required building identifier exists;
- checking whether a lease references the correct occupancy;
- calculating replacement value from area × unit replacement cost;
- applying a known cost index;
- classifying a detention horizon into a defined band;
- validating JSON against a schema.

An AI agent is useful where interpretation is required. Examples:

- rewriting a technical deficiency into a planning opportunity;
- deciding whether several opportunities make sense as one coordinated work package;
- explaining how a lease decision affects an investment recommendation;
- synthesizing a complex building strategy for a reviewer.

**Cookbook rule:** if a rule can be calculated or validated reliably in code, do that before asking an agent to reason about it.

---

## 3. Source data versus canonical data

Operational sources can use different column names, identifiers, units, codes, and structures. The agents should not have to relearn those differences every time.

Therefore:

```text
source field
   -> mapping / crosswalk
   -> canonical field
```

Example:

```text
Cout_Total -> source_total_cost
ID_Immeuble -> building_id
Etat -> condition_rating
```

The source is preserved. The canonical model is the stable language of the pipeline.

This creates an important boundary: **changing a source column should normally require changing a mapping, not rewriting every agent.**

---

## 4. Site context

The agents should not independently search ten datasets and decide which records belong to a building.

A deterministic Site Context Builder first assembles the authorized information for one building into `site_context.json`.

Think of it as the building's **case file**.

It can contain:

- building identity and physical characteristics;
- service points and occupancies;
- deficiencies;
- components;
- accessibility observations;
- leases;
- active projects;
- future initiatives;
- asset strategy;
- detention horizon;
- risk;
- strategic context;
- derived facts;
- source lineage;
- data-quality results.

Once generated, this case file becomes the principal factual input to the agent sequence.

---

## 5. Information products

Each stage should produce something that the next stage can consume.

Do not think of an agent as simply having a conversation. Think of it as a controlled transformation:

```text
Input Information Product
       -> bounded transformation
       -> Output Information Product
```

For example:

```text
deficiencies -> Agent A -> opportunities
opportunities -> Agent B -> work packages
work packages -> Agent C -> costed work packages
```

This makes lineage possible.

---

## 6. Human-in-the-loop does not mean "human at the end"

The human is part of the control system.

The pipeline can stop because information is invalid. A reviewer can approve, modify, defer, reject, or return work. Reviewer feedback can trigger a new version. Source-data conflicts can be sent back upstream rather than silently accepted.

The desired pattern is:

```text
machine structure -> professional judgment -> machine-readable decision -> controlled revision
```

---

# Part III — Start here: choose the scope

## 7. Region, branch, site, building

The desktop application supports hierarchical filtering:

```text
Region
  -> Branch
      -> Site
          -> Building
```

These are selection dimensions. They should not be confused with service-point/occupancy relationships.

A branch may have several sites. A site may contain several buildings. A region may contain many branches.

The final analysis unit remains the **building**.

### Cookbook

1. Run `python app/main.py`.
2. Select one or more regions.
3. Narrow to one or more branches if useful.
4. Narrow to sites if useful.
5. Select individual buildings, or allow all buildings surviving the filters to become the scope.
6. Confirm the number of buildings selected.

If 20 buildings are selected, the application is preparing 20 independent analyses—not one blended 20-building recommendation.

---

# Part IV — Choose how much analysis you actually need

## 8. Analysis depth

Not every building requires maximum analytical complexity.

### Level 0 — Validation only

Use when the question is:

> Do we have trustworthy enough information about this building to analyze it?

No work-package recommendation is required.

### Level 1 — Work Package Analysis

This is the baseline agentic pipeline:

```text
A -> B -> C -> T -> E
```

Use when the principal question is:

> What work packages should be considered for this building?

### Level 2 — Strategic Site Analysis

Adds richer context such as detention horizon, leases/occupancy, projects, initiatives, accessibility, component lifecycle, risk, FCI/replacement-value context, and strategic context.

Use when the question becomes:

> Given what is happening with this building, what is the sensible investment strategy?

### Level 3 — Advanced Investment Analysis

Adds deeper modules such as cost sensitivity, alternatives, timing options, amortization/accounting considerations, and more extensive comparison.

Use selectively on complicated or material sites.

### Custom

Allows an experienced analyst to choose capabilities individually.

---

## 9. Analysis effort

Depth and effort are different concepts.

`RAPID`, `STANDARD`, and `THOROUGH` should have explicit methodological meaning. They should not simply tell an LLM to "think harder."

A future mature implementation might define, for example:

- **Rapid:** focus on material needs and obvious interactions;
- **Standard:** process the normal complete methodology;
- **Thorough:** test alternatives, conflicts, sensitivity, and deeper cross-domain interactions.

The selected configuration is captured in `analysis_manifest.json`.

The manifest is the **recipe card for the run**: what building, what depth, what effort, what modules, what version.

---

# Part V — Phase 0: Source preparation

## 10. Source mappings and crosswalks

Before the agents see anything, operational data must be translated into the canonical model.

### Mappings answer:

> Which source column means which canonical field?

### Crosswalks answer:

> Which source identifier/value corresponds to which canonical identifier/value?

Examples include:

- building identifier crosswalks;
- condition-rating normalization;
- intervention-horizon normalization;
- unit-of-measure normalization;
- Uniformat validation.

### Cookbook checks

Before onboarding a new source:

1. inventory its columns;
2. identify its primary identifier;
3. identify the building/site relationship;
4. map fields to canonical fields;
5. identify controlled-value crosswalks;
6. identify required unit conversions;
7. identify fields that cannot be mapped;
8. version the mapping;
9. test on synthetic or approved sample records;
10. do not ask an LLM to invent missing identifier relationships.

---

# Part VI — Phase 1: Deterministic Data Quality Gate

## 11. Why a gate exists

Bad input should not become polished bad output.

The Data Quality Gate examines whether each source is usable for the selected building.

Typical states include:

- `COMPLETE`
- `PARTIAL`
- `CONFLICT`
- `STALE`
- `NOT_APPLICABLE`
- `MISSING`

Severity is a separate idea:

- `BLOCKING`
- `WARNING`
- `INFORMATIONAL`

This matters because "missing" does not always mean "bad." A lease can legitimately be not applicable to an owned building. Missing strategic context is acceptable because that source is optional. A broken building-to-occupancy association may be blocking.

### Cookbook

For each building:

1. run the gate;
2. inspect blocking conditions first;
3. inspect association conflicts;
4. inspect stale information;
5. distinguish missing from not applicable;
6. decide whether warnings are acceptable for the intended analysis level;
7. stop the agent pipeline if the gate is blocked.

**Never use agent confidence to compensate for a deterministic association error.**

---

# Part VII — Phase 2: Build the canonical site context

## 12. The building case file

After validation, the Site Context Builder assembles all relevant records for one building.

This step protects the agents from having to perform joins and identity resolution themselves.

### What to inspect

Before running Agent A on real data, manually inspect at least the first few `site_context.json` files.

Ask:

- Is this the correct building?
- Are the correct service points attached?
- Are all relevant deficiencies present?
- Are leases attached to the right occupancy?
- Are active projects and future initiatives present?
- Is detention horizon represented correctly?
- Is strategic context clearly identified as contextual rather than authoritative fact?
- Are unknown values still unknown rather than silently filled?

The first production milestone is not "the AI produced an answer." It is:

> We trust the building case file.

---

# Part VIII — Agent A: Deficiency to Opportunity

## 13. Concept

A deficiency is an observation of a problem. An opportunity is a normalized planning object that can participate in investment analysis.

Agent A performs that translation.

### Intent

Create a consistent opportunity for each valid source deficiency while preserving lineage.

### Agent A should

- preserve `deficiency_id`;
- preserve building/component relationships;
- preserve source cost rather than re-estimate it;
- distinguish observation from proposed corrective action;
- normalize terminology;
- create a planning-friendly title/description;
- preserve uncertainty.

### Agent A should not

- bundle several deficiencies into a project;
- decide investment strategy;
- suppress a deficiency because a lease may expire;
- index costs;
- invent missing technical facts;
- decide that an existing project automatically resolves the deficiency.

### Why this boundary matters

If Agent A starts making strategic decisions, later stages cannot tell whether an opportunity disappeared because of normalization or because of strategy.

### Cookbook review

For the first live Agent A runs:

1. compare input deficiency count to opportunity count;
2. verify every opportunity points back to a deficiency;
3. verify source cost has not changed;
4. verify observation/corrective-action meaning is preserved;
5. run the Agent A evaluator;
6. reject outputs that violate stage ownership even if the prose sounds intelligent.

---

# Part IX — Agent B: Clustering, bundling and blending

## 14. Concept

Individual deficiencies are often poor project definitions.

Replacing one rooftop unit, repairing roof penetrations, modifying controls, and coordinating access may be technically separate needs but operationally connected.

Agent B asks:

> Which opportunities should be considered together as a coherent work package?

The approach is inspired by SALVO-style thinking around combining interventions rather than treating every need as an isolated project.

### Bundling

Bundling groups compatible work to gain coordination or delivery efficiency.

Examples:

- several roof-related interventions;
- multiple electrical renewals requiring the same shutdown;
- several accessibility modifications in the same entrance zone.

### Blending

Blending considers whether different types of work should be deliberately coordinated because of timing, strategy, disruption, dependency, or broader intervention logic.

### Agent B should

- consume normalized opportunities;
- preserve all opportunity lineage;
- identify logical clusters;
- explain bundling/blending rationale;
- create candidate work packages;
- identify overlaps with projects/initiatives where the selected analysis profile permits it.

### Agent B should not

- silently delete opportunities;
- change authoritative source facts;
- perform final strategic approval;
- hide a need simply because it overlaps another initiative.

### Cookbook questions

For every candidate work package ask:

1. Which opportunities are included?
2. Why are they together?
3. Would separating them be more rational?
4. Is the relationship technical, temporal, spatial, operational, or strategic?
5. Is anything being duplicated by an existing project?
6. Has any opportunity disappeared without explanation?

---

# Part X — Agent C and the deterministic cost engine

## 15. Concept

Costing should be explainable.

The preferred pattern is not "ask an LLM what this project costs." It is:

```text
known source costs
  + approved indexation rules
  + approved indirect-cost rules
  + explicit assumptions
  -> costed work package
```

Agent C can help interpret and present the costing context, but calculations should remain deterministic wherever possible.

### Possible cost layers

- source/direct cost;
- indexation/escalation;
- professional fees;
- project management;
- contingencies;
- permits/testing/commissioning where applicable;
- taxes or other approved factors where applicable.

### Cookbook

For each costed WP:

1. retain the original cost basis;
2. identify the index used and its date/base;
3. show each indirect factor separately;
4. avoid hidden multipliers;
5. record assumptions;
6. flag missing cost inputs rather than inventing precision;
7. later, at advanced levels, distinguish expected cost from uncertainty ranges.

---

# Part XI — Agent T: Strategic recommendation

## 16. Why Agent T is different

Agent T is where the pipeline moves from **what work exists** to **what should be recommended**.

This is intentionally later than A/B/C because strategy should act on a traceable work-package structure, not mutate raw evidence.

### Possible context for T

Depending on the analysis manifest:

- detention horizon;
- ownership/lease situation;
- lease dates and options;
- service-point occupancy;
- current projects;
- future initiatives;
- accessibility;
- component lifecycle;
- FCI/replacement value;
- risk/compliance;
- amortization;
- strategic context transcription;
- cost and uncertainty.

### Four reasoning layers

A useful discipline for T is:

```text
1. authoritative structured facts
2. deterministic business rules
3. contextual/strategic evidence
4. professional interpretation
```

Do not collapse these into one opaque answer.

### Example

A poor HVAC unit may clearly require replacement technically. But if a lease decision occurs in 18 months, the recommendation may be to maintain safely while coordinating the replacement decision with the lease strategy.

The deficiency still exists. The opportunity still exists. The WP still exists. Strategy changes the recommended action/timing—not history.

### Strategic context

Structured strategic-context transcription is valuable but optional.

It can contain intentions, stakeholder priorities, known changes, constraints, assumptions, and uncertainties.

It may influence reasoning but must not silently overwrite authoritative facts. If a transcript says "we are probably leaving" while the authoritative strategy says retain, that is a conflict requiring resolution, not permission for the agent to pick whichever statement it prefers.

---

# Part XII — Agent E: Executive synthesis

## 17. Concept

Agent E translates the approved analytical structure into a concise decision-oriented summary.

E is **not a second work-package generator**.

Ownership remains:

- B creates work packages;
- C costs them;
- T recommends what to do;
- E explains the resulting picture.

### Agent E should answer

- What is the overall condition/investment story?
- What are the principal recommended work packages?
- What are the material costs?
- What decisions or dependencies matter?
- What needs human attention?

### Agent E should not

- create new WPs;
- remove inconvenient WPs;
- invent new costs;
- resolve source conflicts;
- change T's recommendation without a revision process.

---

# Part XIII — The HTML building datasheet SPA

## 18. Why HTML?

The SPA is the principal human-facing information product.

The reviewer should not need Python, JSON expertise, or direct interaction with agent prompts.

The SPA can present:

- building facts;
- source/data-quality status;
- deficiencies;
- opportunities;
- clusters;
- work packages;
- cost structure;
- recommendations;
- executive synthesis;
- human-review controls.

It also embeds machine-readable JSON so the human-facing artifact can return to the machine workflow without scraping visual text.

---

# Part XIV — Human review

## 19. Review is a formal phase

The reviewer uses the HTML SPA.

Review metadata can include:

- reviewer ID;
- reviewer name/role;
- review start timestamp;
- completion timestamp;
- overall review status;
- completion confirmation;
- decision per WP;
- comments;
- scope/cost/timing/risk review flags;
- audit events.

Typical decisions include:

- `APPROVE`
- `APPROVE_WITH_CHANGES`
- `RETURN_FOR_REVISION`
- `DEFER`
- `REJECT`

### Cookbook for reviewers

For each WP:

1. confirm the need is recognizable;
2. inspect source lineage;
3. inspect why items were bundled/blended;
4. inspect cost basis;
5. inspect strategic recommendation;
6. record a decision;
7. write actionable comments where revision is required;
8. confirm completion only when all required WPs have been addressed.

The SPA updates embedded review metadata and preserves timestamps/audit events.

---

# Part XV — Versioned SPA lifecycle

## 20. Never overwrite reviewed history

The repository defines:

```text
spa_exchange/
  generated/
  under_review/
  reviewed/
  extracted/
  revised/
  archived/
```

A typical lifecycle is:

```text
BLDG-001.datasheet.v1.0.html
   -> human review
BLDG-001.datasheet.v1.0.html [review metadata embedded]
   -> feedback extraction
   -> revision
BLDG-001.datasheet.v1.1.html
   -> human review
```

A major methodological or scope change may justify `v2.0`; smaller review-driven revisions may use `v1.1`, `v1.2`, etc.

The exact versioning policy should eventually be formalized, but the core rule already applies: **do not destroy the prior reviewed artifact.**

---

# Part XVI — Agent R: controlled revision

## 21. Concept

The reviewed SPA may be fed back into the agentic workflow.

But the revision agent should not read the HTML visually and improvise. The preferred process extracts the embedded structured data:

```text
reviewed SPA
   -> embedded site context
   + embedded review metadata
   -> review_feedback.json
   -> Agent R
```

### Agent R should

- interpret explicit reviewer decisions/comments;
- identify requested scope/timing/recommendation changes;
- preserve the previous version;
- produce a revision log;
- route cost changes back through costing;
- route strategic changes back through T where appropriate;
- identify comments that actually require source-data correction.

### Agent R should not

- overwrite authoritative source facts because a comment says so;
- erase the prior recommendation;
- hide rejected content from history;
- recalculate cost informally if deterministic costing is required.

### Revision routing examples

```text
"Add the entrance operator to this WP"
    -> scope revision
    -> possibly Agent B / WP revision
    -> Agent C recost

"Cost seems too low"
    -> cost review
    -> Agent C / deterministic cost rules

"Do not replace before lease decision"
    -> strategic timing review
    -> Agent T

"The building area is wrong"
    -> source-data correction
    -> mapping/source layer
    -> rebuild site context
```

This routing discipline is essential.

---

# Part XVII — Optional capabilities

## 22. Accessibility

Accessibility is not simply another deficiency list. It may contain compliant, non-compliant, and unknown criteria.

Unknown must remain unknown. The system should not turn an incomplete assessment into a false non-compliance or false compliance.

Accessibility can influence bundling when work already affects an entrance, washroom, circulation route, etc.

---

## 23. Component lifecycle

Component data provides installation year, condition, useful life, replacement value, and criticality.

It helps distinguish:

- isolated observed failure;
- broader end-of-life renewal;
- timing opportunities across related systems.

Do not assume useful life is a deterministic failure date. It is planning evidence.

---

## 24. Projects and initiatives

An existing project and a future initiative are not the same thing.

A project may already have approved scope/budget and can create duplication risk.

An initiative may represent future intent and create a coordination opportunity.

Neither should silently delete a deficiency. The relationship should be explicit.

---

## 25. Lease and occupancy strategy

Lease facts belong to the relevant business occupancy/service point, not automatically to the entire building.

This is especially important for multioccupant buildings.

A lease expiry for one occupant does not necessarily mean the entire building will be vacated.

The canonical relationships must therefore be preserved before strategic reasoning.

---

## 26. Detention horizon

Detention horizon means the expected period for which the asset/site is intended to remain in the strategy.

Typical canonical bands can support rules such as:

```text
< 2 years
2-5 years
> 5 years
```

The exact business rules belong in versioned rule definitions. The agent should consume those rules, not invent new thresholds.

---

## 27. FCI and replacement value

Replacement value provides scale. FCI can provide a normalized view of condition-related need relative to replacement value.

These metrics can help Agent T contextualize whether a work package is isolated maintenance or part of a broader reinvestment problem.

They should not automatically determine the answer without considering strategy and evidence.

---

## 28. Cost sensitivity and alternatives

At advanced levels, the system may compare uncertainty ranges or alternative intervention strategies.

Examples:

- repair versus replacement;
- minimum intervention versus coordinated renewal;
- current-year intervention versus deferred intervention;
- expected cost versus higher-confidence budget allowance.

These features should be activated intentionally rather than applied to every site by default.

---

# Part XVIII — What the orchestrator is supposed to do

## 29. Orchestration is traffic control

The orchestrator should not become an all-knowing super-agent.

Its role is to:

1. read the analysis manifest;
2. confirm the Data Quality Gate permits execution;
3. identify which modules are enabled;
4. provide the correct information product to each stage;
5. enforce sequence/dependencies;
6. record versions and outputs;
7. stop or escalate when a stage fails its contract.

Eventually:

```text
analysis_manifest.json
        ↓
Orchestrator
        ├─ Level 0? stop after validation/context
        ├─ Level 1? execute A-B-C-T-E
        ├─ Level 2? activate strategic capabilities
        ├─ Level 3? activate advanced capabilities
        └─ Custom? execute selected compatible modules
```

The manifest should control functionality—not ad hoc prompt wording.

---

# Part XIX — Testing agents without testing prose

## 30. Why exact-text testing is wrong

Two good model runs can use different wording.

Therefore the evaluation harness should test business invariants.

Examples:

- every deficiency remains traceable;
- Agent A does not change source cost;
- Agent B does not lose opportunities;
- lease expiry is surfaced when applicable;
- unknown accessibility remains unknown;
- existing project overlap is recognized;
- blocked association data never reaches Agent A;
- Agent E does not create new WPs.

This allows prompts or models to evolve while protecting the methodology.

---

# Part XX — A complete cookbook run

## 31. Recipe: one normal building

### Ingredients

- mapped source data;
- valid building identifier;
- deficiencies;
- relevant optional sources;
- approved business rules;
- selected analysis profile.

### Method

**Step 1 — Select scope**

Choose region/branch/site/building. Confirm one building.

**Step 2 — Choose profile**

Start with Level 1 / Standard unless the business question requires more.

**Step 3 — Validate**

Run the Data Quality Gate. Stop on blocking errors.

**Step 4 — Build site context**

Generate and inspect `site_context.json`.

**Step 5 — Generate manifest**

Record requested profile, effort, capabilities, requester, and versions.

**Step 6 — Run Agent A**

Normalize deficiencies to opportunities. Run invariant checks.

**Step 7 — Run Agent B**

Create clusters/work packages. Inspect lineage and rationale.

**Step 8 — Run Agent C**

Apply deterministic costing and document assumptions.

**Step 9 — Run Agent T**

Apply the selected strategic context and business rules.

**Step 10 — Run Agent E**

Produce the executive synthesis without modifying WP ownership.

**Step 11 — Generate SPA**

Create the versioned building datasheet with embedded machine-readable context/review metadata.

**Step 12 — Human review**

Reviewer records decisions/comments and confirms completion.

**Step 13 — Process feedback**

If approved, preserve the reviewed artifact. If changes are required, extract structured feedback.

**Step 14 — Agent R / routing**

Route changes to the correct stage and generate a new version.

**Step 15 — Re-review**

Review v1.1/v2.0 as required.

### Finished product

A traceable, reviewed site-level investment information product—not merely an AI response.

---

# Part XXI — Recipe: batch of buildings

## 32. Batch does not mean blended

Suppose a user selects:

- one region;
- three branches;
- eight sites;
- twelve buildings.

The same analysis configuration can be applied to all twelve, but the system should create twelve independent manifests and twelve independent analysis chains.

### Why

Each building can have different:

- DQ status;
- detention horizon;
- lease situation;
- deficiencies;
- strategic context;
- reviewer;
- revision history.

The batch is an operational convenience, not a portfolio optimizer.

---

# Part XXII — Common failure modes

## 33. "The agent can figure out the joins"

Do not rely on this. Resolve building/service-point/occupancy/lease associations deterministically.

## 34. "Missing means zero"

It does not. Missing, not applicable, unknown, and zero are different states.

## 35. "The summary looks good, so the pipeline worked"

A polished summary can hide lineage loss. Inspect contracts and evaluators.

## 36. "Let Agent T fix bad data"

Do not. T interprets strategy; it is not a data-cleansing substitute.

## 37. "The reviewer changed the area in a comment, so update the area"

Route that comment to the authoritative source-data correction process.

## 38. "One maximum-complexity profile for every building"

Avoid unnecessary cost and cognitive complexity. Use the lowest analysis depth that answers the decision question.

## 39. "Work package equals project"

Not necessarily. A work package is a planning information product. It may later become, join, split into, or inform one or more delivery projects.

---

# Part XXIII — How to introduce this solution to a new team member

## 40. Suggested learning sequence

Do not begin by teaching prompts.

Teach in this order:

1. **The business problem** — fragmented evidence must become a reviewed investment recommendation.
2. **The building case file** — understand `site_context.json` conceptually.
3. **Deterministic versus agentic** — know what AI is and is not allowed to decide.
4. **A/B/C/T/E** — understand stage ownership.
5. **The SPA** — understand the human information product.
6. **Review/revision** — understand how human judgment returns to the pipeline.
7. **Analysis profiles** — understand how complexity is selected.
8. **Mappings/contracts/rules** — only then go deeper into implementation.
9. **Prompts and code** — implementation detail after methodology is understood.

A user should be able to explain the methodology without mentioning a specific LLM model.

---

# Part XXIV — Roles in the operating model

## 41. Data steward / integration analyst

Owns mappings, crosswalks, source quality, canonical compatibility, and unresolved associations.

## 42. Planning analyst / site analyst

Selects buildings, chooses analysis depth, inspects readiness, runs/coordinates analysis, and interprets outputs.

## 43. Subject-matter expert

Provides technical judgment for specific domains and may review relevant work packages.

## 44. Reviewer / approver

Uses the SPA to make explicit decisions, provide comments, and confirm completion.

## 45. Methodology owner

Owns business rules, analysis profiles, agent boundaries, evaluation invariants, and versioning policy.

## 46. Developer / automation owner

Implements deterministic functions, orchestration, schemas, interfaces, tests, and safe agent integration.

One person may hold several roles in an early prototype, but the responsibilities should remain conceptually distinct.

---

# Part XXV — Governance checklist

## 47. Before changing an agent

Ask:

- Is this actually an agent problem or a deterministic-rule problem?
- Which stage owns this decision?
- Does the output contract need to change?
- Will lineage remain intact?
- What evaluator should protect the new behavior?
- Does the analysis profile/capability registry need to expose the feature?

## 48. Before adding a data source

Ask:

- What decision does this source improve?
- Is it authoritative, contextual, or derived?
- What is its building/site/service-point relationship?
- Is it required or optional?
- What makes it stale?
- What conflicts can it create?
- Which agents are authorized to use it?

## 49. Before adding a new agent

Ask whether the capability can instead be:

- a deterministic function;
- a reusable capability;
- a rule set;
- an extension of an existing bounded agent.

Agent proliferation should be avoided.

---

# Part XXVI — Where this product stops

## 50. Site analysis versus portfolio planning

This repository answers:

> For this building, what are the reviewed and traceable work packages and recommendations?

It intentionally does not yet answer:

> Given all buildings, limited annual CAPEX and delivery capacity, which projects should the organization execute in each year?

That downstream problem belongs to a portfolio/scenario/optimization layer consuming approved site-level work-package information products.

This separation is deliberate.

---

# Part XXVII — Mental model to remember

If only one diagram is remembered, use this:

```text
TRUST THE DATA
Mappings -> Quality Gate -> Site Context

UNDERSTAND THE NEED
Agent A -> Opportunities

DESIGN THE INTERVENTION
Agent B -> Work Packages

UNDERSTAND THE MONEY
Agent C -> Costed Work Packages

MAKE THE SITE DECISION
Agent T -> Recommendation

COMMUNICATE THE DECISION
Agent E -> Executive Synthesis

PUT A HUMAN IN CONTROL
HTML SPA -> Review Metadata

LEARN FROM THE REVIEW
Feedback -> Agent R -> New Version

PRESERVE HISTORY
Versioning + Lineage + Audit Trail
```

The system is successful when a reviewer can understand **what is recommended, why it is recommended, what evidence supports it, what rules were applied, what uncertainty remains, who reviewed it, and what changed between versions.**

That is the core objective of the architecture.
