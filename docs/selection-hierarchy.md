# Selection Hierarchy

The analysis interface supports hierarchical, cumulative multi-filter selection:

```text
Region
  -> Branch
      -> Site
          -> Building / physical premises
```

A region may contain multiple branches. A branch may contain multiple sites. A site may contain one or multiple physical buildings/premises. The hierarchy is used to define the scope of a batch analysis; it does not change the building/physical-premises analysis unit.

## Important distinction: selection hierarchy vs occupancy model

The hierarchy above describes how users locate and select physical assets for analysis.

It is separate from the business-occupancy relationship:

```text
Transit / Service Point
        <-> Temporal Occupancy
                <-> Site + Building/Premises
                        <-> Lease only where applicable
```

A transit/service point is a business identity, not a permanent place identifier. It can move from one physical building/site to another over time through dated occupancy relationships. Multiple transits may coexist at one site.

A site can also contain both owned and leased portions. Therefore do not assume:

```text
one site = one transit
one site = one building
one site = one tenure type
```

See `docs/identity-and-occupancy-model.md` for the canonical identity principles.

Do not use `service_point_id` or a transit number as a substitute for `site_id`, `branch_id`, or `building_id`.

## Selector behavior

All filters are cumulative and multi-select:

- zero selected values at a level means all values at that level;
- selecting one or more regions limits available branches;
- branch selections limit available sites;
- site selections limit available buildings/premises;
- the user may optionally refine the final building list;
- if no individual buildings are selected, every building surviving the higher-level filters is in scope.

Examples:

```text
REG-EAST
  -> all branches
  -> all sites
  -> 24 buildings in scope
```

```text
REG-EAST + REG-CENTRE
  -> BRANCH-01 + BRANCH-07
  -> all sites in those branches
  -> 11 buildings in scope
```

```text
BRANCH-04
  -> SITE-A + SITE-C
  -> BLDG-101 + BLDG-107 + BLDG-109
```

## Execution behavior

A batch scope is only a selection convenience. Each resulting building receives its own:

- Data Quality Gate result;
- canonical site context;
- analysis manifest;
- agent artifacts;
- versioned HTML SPA;
- human review metadata;
- revision history.

This preserves building-level traceability while allowing efficient processing of many sites/buildings.

## Canonical hierarchy fields

The canonical building/premises record may carry:

- `region_id`
- `branch_id`
- `site_id`
- `building_id`

These identifiers may be populated through source mappings and deterministic crosswalks when operational systems use different names or keys. Source systems do not need to be physically renamed to match the canonical model.

Transit/service-point identifiers belong to the occupancy/business domain and should be joined temporally rather than copied into the hierarchy as physical identifiers.