# Identity, Transit, Site, Building and Occupancy Model

## Why this model exists

Operational real-estate data often contains several identifiers that appear to describe the same place but actually describe different concepts. This is a major integration risk.

In particular, a **transit number must not be treated as a permanent physical-site or building identifier**.

A transit represents a business/service-point identity that can move over time. A physical building remains where it is. A site can contain more than one physical/tenure portion, and multiple transits can coexist at the same site.

The onboarding and Data Quality Gate must therefore model these concepts separately and preserve their history.

## Core concepts

### Region
Organizational/geographic grouping used for filtering and scope selection.

### Branch
Organizational grouping below a region. A branch can contain multiple sites.

### Site
A logical/location-level real-estate grouping. A site is not necessarily equivalent to one building, one transit, or one tenure arrangement.

A site can contain:
- one or multiple buildings/physical premises;
- an owned portion;
- a leased portion;
- both owned and leased portions simultaneously;
- one or multiple transits/service points.

### Building / physical premises
The physical real-estate asset or premises to which technical evidence such as deficiencies, components and building characteristics should be associated.

The physical asset identity should remain stable even if the business transit occupying it changes.

### Transit / service point
A business/service-point identity. It is **mobile through time**.

A transit may:
- occupy Building A during one period;
- later move to Building B;
- occupy owned premises at one time;
- later occupy leased premises;
- coexist at a site with another transit.

Therefore:

```text
transit_id != site_id
transit_id != building_id
```

### Occupancy
The temporal relationship connecting a transit/service point to a physical premises or site portion.

This is the critical bridge entity.

Conceptually:

```text
transit
   + building/premises
   + site
   + effective_from
   + effective_to
   + tenure context
   = occupancy relationship
```

A transit's current building must be derived from the active occupancy relationship, not assumed from the transit number itself.

### Lease
A lease is associated with the applicable leased occupancy/premises relationship. It should not automatically be interpreted as applying to the entire site or building.

### Tenure / ownership portion
Tenure should be modeled at the level at which it is actually true.

Do not assume that `site.tenure = OWNED` or `site.tenure = LEASED` is sufficient when a single site contains both owned and leased portions.

Where required, introduce a premises/portion relationship such as:

```text
premises_id
site_id
building_id
tenure_type = OWNED | LEASED | MIXED/OTHER
area
valid_from
valid_to
```

This permits one site to contain an owned part and a leased section without corrupting the physical building or business-service-point identities.

## Example

```text
REGION R01
  |
  +-- BRANCH BR07
        |
        +-- SITE S100
              |
              +-- Premises P100-A [OWNED]
              |      |
              |      +-- Transit T001 [active occupancy]
              |
              +-- Premises P100-B [LEASED]
                     |
                     +-- Transit T002 [active occupancy]
```

Later, Transit T001 may move:

```text
T001
  2024-01-01 -> 2027-06-30 : P100-A / Site S100
  2027-07-01 -> current    : P205-C / Site S205
```

The transit identity remains T001. The occupancy relationship changes.

## Canonical relationship model

Preferred conceptual structure:

```text
Region -> Branch -> Site
                    |
                    +-> Premises / Building Portion -> Building
                    |            |
                    |            +-> Tenure
                    |
                    +-> Occupancy <- Transit / Service Point
                           |
                           +-> effective dates
                           +-> Lease when applicable
```

Depending on the real source systems, `premises` may be a formal canonical entity or may initially be represented through occupancy/building/lease relationships. Do not invent it automatically; Agent M should determine whether the real data requires this explicit layer.

## Mapping rules for Agent M

During real-data onboarding, Agent M must ask separately:

1. Which field uniquely identifies a transit/service point?
2. Which field uniquely identifies a site?
3. Which field uniquely identifies a physical building/premises?
4. Where is the transit-to-building relationship stored?
5. Does that relationship contain effective start/end dates?
6. Can one transit have historical records at several buildings?
7. Can multiple transits be active at one site?
8. Can a site contain both owned and leased premises?
9. At what level is tenure authoritative: site, building, premises, occupancy or lease?
10. Which source is authoritative for current occupancy?
11. Which source is authoritative for occupancy history?
12. Which source is authoritative for lease dates?

Agent M must not approve the identity backbone until these questions are understood sufficiently for deterministic association.

## Data Quality Gate rules

The Data Quality Gate should eventually test conditions such as:

- a transit has more than one active occupancy when this is not allowed by the business model;
- overlapping occupancy periods exist unexpectedly;
- a lease is attached to an owned premises without an explained mixed-tenure relationship;
- a transit points directly to a building but contradicts the authoritative occupancy source;
- a site-level tenure value conflicts with premises-level evidence;
- a deficiency is joined to a transit when the authoritative relationship should be to the physical building;
- an occupancy lacks effective dates where history is required;
- a current occupancy cannot be resolved deterministically.

These should be explicit `CONFLICT`, `WARNING`, or `BLOCKING` results according to the approved business rules.

## Implication for site analysis

Technical evidence belongs primarily to the physical asset/premises:

```text
deficiency -> building/premises
component -> building/premises
accessibility -> assessed physical scope
```

Business strategy may belong to the transit/service point:

```text
transit strategy
lease expiry
relocation intent
business occupancy requirement
```

Agent T may reason across these domains only after the temporal occupancy relationship has connected them correctly.

Example:

> A roof deficiency belongs to Building B100. Transit T001 currently occupies part of B100, but the transit is scheduled to move. The deficiency does not disappear when T001 moves; only the investment recommendation may change depending on ownership, future occupancy and asset strategy.

## Historical principle

Never overwrite history by replacing a transit's old building with its new building.

Represent movement as dated relationships.

This allows future questions such as:

- Which transit occupied this building when a deficiency was observed?
- Which building did this transit occupy when a lease decision was made?
- Was the recommended work intended for an owned or leased portion at the time of analysis?
- Did the transit move after the work package was approved?

## Governing rule

**Physical identity, business identity, location identity, tenure and time are separate dimensions.**

The pipeline may combine them for analysis, but the canonical model and onboarding mappings must never collapse them into a single convenient identifier.