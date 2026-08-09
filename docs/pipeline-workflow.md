# Agentic Construction Work Package Pipeline

This view summarizes the source normalization, deterministic validation, agent sequence, HTML SPA human review, versioning, and revision loop.

```mermaid
flowchart TD

    A[Operational Source Data<br/>Buildings / Service Points / Occupancies / Deficiencies / Components / Accessibility / Initiatives / Projects / Leases / Strategic Context]
    B[Source Mappings + Crosswalks<br/>Versioned deterministic transformations]
    C[Canonical Data Model]
    D[Data Quality Gate<br/>COMPLETE / PARTIAL / CONFLICT / STALE / N-A / MISSING]
    E{Blocking issue?}

    A --> B --> C --> D --> E
    E -- Yes --> E1[BLOCKED<br/>Human correction required]
    E1 --> B
    E -- No --> F[Site Context Builder]
    F --> G[site_context.json<br/>Canonical per-building information product]

    G --> H[Agent A<br/>Deficiencies to Opportunities]
    H --> I[opportunities.json]
    I --> J[Agent B<br/>Clustering / Bundling / Blending<br/>SALVO-inspired]
    J --> K[Candidate Work Packages]
    K --> L[Agent C + Deterministic Cost Engine<br/>Indexation + Indirect Costs]
    L --> M[Costed Work Packages]
    M --> N[Agent T<br/>Strategic Work Recommendations]
    N --> O[Recommended Work Packages]
    O --> P[Agent E<br/>Executive Synthesis]
    P --> Q[Building Information Product]

    Q --> R[HTML Building Datasheet SPA<br/>Embedded site_context + review_metadata]
    R --> S[Human Review Panel]

    S --> S1[Reviewer ID]
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

    X --> Y[Agent R<br/>Review Revision Agent]
    Y --> Z{Revision requirement}

    Z -- Scope / Recommendation --> ZA[Revise Work Package / Recommendation]
    Z -- Cost Impact --> ZB[Re-run Deterministic Cost Engine]
    Z -- Timing / Strategy --> ZC[Re-run Agent T]
    Z -- Source Fact Conflict --> ZD[Human / Source Data Correction Required]

    ZA --> ZE[Revised Artifact]
    ZB --> ZE
    ZC --> ZE
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
    K -. work package lineage .-> L
    M -. cost lineage .-> N
    O -. recommendation lineage .-> P
    T -. reviewer traceability .-> X
    X -. revision lineage .-> Y
```

## Core feedback loop

`Source data -> deterministic validation -> agents -> SPA -> human review -> structured feedback -> Agent R -> revised SPA -> human review`

Reviewer feedback is evidence and instruction for revision. It does not silently replace authoritative source facts. A conflict with source data is routed back to the source/mapping/validation layer.
