# Information Model V0.2

This document defines a synthetic reference information model for a site-level building investment planning pipeline. It intentionally contains no employer-confidential data.

## Core principle

Treat each source as a domain connected through explicit identifiers rather than as independent spreadsheets.

Primary entities:

- `building_id`: physical building or leased premises record.
- `service_point_id`: business/service entity occupying all or part of a building.
- `occupancy_id`: relationship between a service point and a building over time.
- `lease_id`: lease tied to an occupancy/service point and building.
- `deficiency_id`: observed condition issue tied to a building and optionally to a component.
- `component_id`: maintainable building system/component.
- `initiative_id`: known future initiative or opportunity.
- `project_id`: approved or active project.

## Source domains

### 1. Buildings
Physical/site master data.

Typical fields:
- building_id
- building_name
- address
- municipality
- province
- postal_code
- ownership_type: owned / leased / mixed
- construction_year
- gross_area_sqft
- number_of_floors
- replacement_cost_per_sqft
- calculated_replacement_value
- flood_risk_rating
- portfolio_status
- latitude / longitude when available
- source_system
- source_record_id
- effective_date

Replacement value should be deterministic: `gross_area_sqft * replacement_cost_per_sqft` unless an authoritative replacement value is supplied.

### 2. Service points and occupancies
A service point is a business entity, not a building. A building may host zero, one, or many service points over time.

Typical fields:
- service_point_id
- service_point_name
- business_entity_type
- occupancy_id
- building_id
- occupancy_role: owner_occupant / tenant / subtenant / shared
- occupancy_start_date
- occupancy_end_date
- area_occupied_sqft
- is_primary_occupant

This relation is critical because lease decisions apply to occupancies/business entities while physical deficiencies apply to buildings.

### 3. Deficiencies / FCA observations
Primary work-generation source.

Typical fields:
- deficiency_id
- building_id
- component_id if known
- title
- uniformat_code
- uniformat_level
- action_type: maintenance / repair / replacement / investigation
- unit_cost
- unit_of_measure
- quantity
- source_total_cost
- observation
- proposed_corrective_action
- intervention_horizon
- condition_rating: good / fair / poor / very_poor
- inspection_date
- source_system
- source_record_id

### 4. Components / asset register
Maintainable systems and assets.

Typical fields:
- component_id
- building_id
- asset_type
- uniformat_code
- description
- manufacturer/model when available
- installation_year
- condition_rating
- useful_life_years
- expected_end_of_life_year
- replacement_value
- quantity
- unit_of_measure
- criticality

### 5. Universal accessibility criteria
Structured criteria by building, entrance, space, or service point when relevant.

Typical fields:
- accessibility_assessment_id
- building_id
- criterion_code
- criterion_description
- compliant: true / false / unknown
- assessment_date
- observation
- corrective_action_if_known
- priority

Do not collapse `unknown` into `false`.

### 6. Future initiatives / identified opportunities
Known future interventions that may overlap with deficiencies and should influence bundling/blending.

Typical fields:
- initiative_id
- building_id
- service_point_id if business-driven
- title
- description
- initiative_type
- status
- target_start_year
- target_end_year
- rough_order_cost
- strategic_driver
- dependencies

### 7. Projects
Approved, planned, active, or recently completed projects used to prevent duplicate scope and expose dependencies.

Typical fields:
- project_id
- building_id
- service_point_id if relevant
- title
- project_status
- planned_start_date
- planned_end_date
- approved_budget
- forecast_cost
- scope_summary
- included_uniformat_codes
- related_initiative_id

### 8. Leases
Lease data must preserve the distinction between physical building and occupying business entity.

Typical fields:
- lease_id
- building_id
- service_point_id
- occupancy_id
- lease_start_date
- lease_end_date
- renewal_option_date
- notice_date
- lease_status
- leased_area_sqft
- landlord_or_tenant_role

A lease-end trigger should therefore flow through `lease -> occupancy -> service point -> building`, not through building alone.

## Additional source domains already discussed or strongly recommended

### 9. Portfolio risk / compliance
Examples: flood, health and safety, regulatory exposure, asbestos probability, reputational/operational risk. Flood risk may remain on Building for V0.2, but a dedicated risk table scales better when multiple risk types exist.

### 10. Energy / carbon / building performance
Examples: kWh/m2, utility consumption, emissions, carbon targets, BFI/energy performance indicators. These should later influence strategy and prioritization but should not be invented by work-package agents.

### 11. Financial / asset strategy
Examples: retention horizon, owner-vs-tenant strategy, amortization status, capital constraints, replacement value, FCI, budget envelope. This is essential for Agent T recommendations.

### 12. Maintenance / CMMS history
Work orders, recurring failures, preventive maintenance, breakdown frequency, asset downtime, and maintenance cost history. This improves confidence that an apparent deficiency is isolated or systemic.

### 13. Space / occupancy / utilization
Area by occupant, vacancy, utilization, capacity, and consolidation opportunities. Useful when a building investment is being compared against relocation or footprint reduction.

### 14. BIM / spatial / GIS references
Model identifiers, floor/space IDs, coordinates, geometry references, 360 imagery, and other location evidence. These are not required for V0.2 execution but are important lineage/context sources.

## Association hierarchy

Preferred joins:

1. Exact authoritative ID.
2. Approved crosswalk table.
3. Composite deterministic key explicitly documented.
4. Fuzzy matching only as a flagged exception requiring human validation.

Never silently join using only building name or street address.

## V0.2 pipeline run

Each execution should create a `pipeline_run.json` containing:

- run_id
- site/building scope
- source snapshots and versions
- data-quality results
- association exceptions
- rule versions
- prompt/agent versions
- stage states
- generated artifact paths
- human approvals
- timestamps
- unresolved exceptions

The run manifest becomes the auditable spine of the entire pipeline.