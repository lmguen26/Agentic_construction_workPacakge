# Agentic Construction Work Package Pipeline

This view summarizes the current building-level workflow: real-data onboarding, canonical identity resolution, deterministic validation, configurable analysis, A-B-C-T-E transformation, HTML SPA human review, versioning, and controlled revision.

> Canonical identity rule: `Region -> Branch -> Site -> Building` is the selection hierarchy. Transit/service-point identity is connected to physical premises through temporal occupancy and lease relationships; it is not a substitute for `building_id`.

```mermaid
flowchart TD

    A[Operational Source Data<br/>Hierarchy / Buildings / Transits-Service Points / Occupancies / Premises if needed / Deficiencies / Components / Accessibility / Initiatives / Projects / Leases / Strategy / Strategic Context]
    AM[Agent M<br/>Guided real-data onboarding facilitator]
    B[Mappings + Crosswalks<br/>Human-approved semantic and identity relationships]
    C[Canonical Data Model]
    ID[Identity & Temporal Association Layer<br/>Region → Branch → Site → Building<br/>Transit ↔ Occupancy ↔ Premises/Building ↔ Lease]
    D[Deterministic Data Quality Gate<br/>COMPLETE / PARTIAL / CONFLICT / STALE / NOT_APPLICABLE / MISSING]
    E{Blocking issue?}

    A --> AM --> B --> C --> ID --> D --> E
    E -- Yes --> E1[BLOCKED<br/>Source / mapping / relationship correction]
    E1 --> B
    E -- No --> F[Site Context Builder]
    F --> G[site_context.json<br/>Canonical information product for one building_id]

    G --> CP[Site Analysis Cockpit]
    CP --> MAN[analysis_manifest.json<br/>Level 0 / 1 / 2 / 3 / Custom<br/>Rapid / Standard / Thorough]
    MAN --> LV{Profile requires agentic work-package analysis?}

    LV -- Level 0 --> Q0[Validated Building Datasheet / Context Only]

    LV -- Yes --> H[Agent A<br/>Deficiencies → Opportunities]
    H --> I[opportunities.json<br/>stage = OPPORTUNITIES]
    I --> J[Agent B<br/>Clustering / Bundling / Blending<br/>SALVO-inspired]
    J --> K[Work Packages<br/>stage = CLUSTERED]
    K --> L[Deterministic Cost Engine + Agent C<br/>Indexation + Indirect Costs]
    L --> M[Costed Work Packages<br/>stage = COSTED]
    M --> N[Agent T<br/>Strategic Recommendation<br/>using manifest-authorized context]
    N --> O[Recommendations<br/>stage = RECOMMENDED]
    O --> P[Agent E<br/>Executive Synthesis only]
    P --> Q[Building Summary<br/>stage = SUMMARIZED]

    Q0 --> R[Versioned HTML Building Datasheet SPA]
    Q --> R
    R --> R0[Embedded site_context + analysis metadata + review_metadata]
    R0 --> S[Human Review Panel]

    S --> S1[Reviewer ID / Role]
    S --> S2[Start / Completion Timestamps]
    S --> S3[Work Package Decision]
    S --> S4[Comments + Scope / Cost / Timing / Risk Flags]
    S --> S5[Completion Confirmation]
    S --> S6[Audit Events]

    S1 --> T[Embedded Review Metadata JSON]
    S2 --> T
    S3 --> T
    S4 --> T
    S5 --> T
    S6 --> T

    T --> U[Reviewed Versioned SPA]
    U --> V[spa_exchange/reviewed/]
    V --> W[Review Feedback Extractor]
    W --> X[review_feedback.json]

    X --> Y[Agent R<br/>Controlled Review Revision / Routing]
    Y --> Z{Owning layer for requested change}

    Z -- Work-package structure --> ZA[Return to Agent B / bounded WP revision]
    Z -- Cost impact --> ZB[Re-run deterministic costing + C interpretation]
    Z -- Timing / Strategy --> ZC[Return to Agent T]
    Z -- Summary only --> ZS[Regenerate Agent E summary]
    Z -- Source fact conflict --> ZD[Source / Mapping / Canonical Data Correction]

    ZA --> ZE[Revised Artifact]
    ZB --> ZE
    ZC --> ZE
    ZS --> ZE
    ZD --> B

    ZE --> ZF[Generate New SPA Version<br/>v1.1 / v1.2 / v2.0]
    ZF --> R

    R --> AA[spa_exchange/generated/]
    AA --> AB[spa_exchange/under_review/]
    AB --> V
    W --> AC[spa_exchange/extracted/]
    ZE --> AD[spa_exchange/revised/]
    U --> AE[spa_exchange/archived/]

    G -. source lineage .-> H
    I -. opportunity lineage .-> J
    K -. work-package lineage .-> L
    M -. cost lineage .-> N
    O -. recommendation lineage .-> P
    T -. reviewer traceability .-> X
    X -. revision lineage .-> Y
```

## Batch selection

The cockpit may select multiple regions, branches, sites and buildings. A batch selection is operational convenience only:

```text
one batch selection
    -> building run 1
    -> building run 2
    -> building run 3
    -> ...
```

Each building keeps an independent `analysis_manifest`, pipeline run, SPA, review and revision history.

## Core feedback loop

`Trusted canonical data -> configured analysis -> agents -> SPA -> human review -> structured feedback -> controlled routing/revision -> new SPA -> human review`

Reviewer feedback is evidence and instruction for revision. It does not silently replace authoritative source facts. A conflict with source data is routed back to the source/mapping/canonical layer.