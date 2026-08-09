# Selection Hierarchy

The analysis interface supports hierarchical, cumulative multi-filter selection:

```text
Region
  -> Branch
      -> Site
          -> Building
```

A region may contain multiple branches. A branch may contain multiple sites. A site may contain one or multiple buildings. The hierarchy is used to define the scope of a batch analysis; it does not change the building as the atomic execution and review unit.

## Important distinction: selection hierarchy vs occupancy model

The hierarchy above describes how users locate and select physical assets for analysis.

It is separate from the business-occupancy relationship:

```text
Service Point
    <-> Occupancy
        <-> Building
            <-> Lease where applicable
```

A building can therefore contain multiple service points even though it belongs to one selection hierarchy path. Likewise, a service point may move between buildings over time through occupancy records.

Do not use `service_point_id` as a substitute for `site_id`, `branch_id`, or `building_id`.

## Selector behavior

All filters are cumulative and multi-select:
- zero selected values at a level means all values at that level;
- selecting one or more regions limits available branches;
- branch selections limit available sites;
- site selections limit available buildings;
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

This preserves site-level traceability while allowing efficient processing of tens of buildings.

## Canonical hierarchy fields

The canonical building record may carry:
- `region_id`
- `branch_id`
- `site_id`
- `building_id`

These identifiers may be populated through source mappings and deterministic crosswalks when operational systems use different names or keys. Source systems do not need to be physically renamed to match the canonical model.