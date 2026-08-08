# Information Model V0.2

This document defines a synthetic reference information model for a site-level building investment planning pipeline. It intentionally contains no employer-confidential data.

## Core principle
Treat each source as a domain connected through explicit identifiers rather than as independent spreadsheets.

Primary entities: `building_id`, `service_point_id`, `occupancy_id`, `lease_id`, `deficiency_id`, `component_id`, `initiative_id`, and `project_id`.

## Canonical terminology
- Use **detention horizon / horizon de détention** throughout the model.
- Canonical field: `detention_horizon_years`.
- Do not use `retention_horizon`.

## Source domains

### 1. Buildings
One record per physical building/premises.

Suggested fields:
- building_id
- building_name
- building_status
- ownership_type: owned / leased / mixed
- building_type
- address
- municipality
- province
- postal_code
- latitude / longitude
- construction_year
- major_renovation_year
- gross_area_sqft
- number_of_floors
- number_of_basements
- site_area_sqft
- replacement_cost_per_sqft
- calculated_replacement_value
- replacement_value_date
- flood_risk_rating
- overall_risk_rating
- fci
- bfi
- condition_rating
- detention_horizon_years
- asset_strategy
- strategic_status
- source_system
- source_record_id
- effective_date

Replacement value should be deterministic: `gross_area_sqft * replacement_cost_per_sqft` unless an authoritative replacement value is supplied.

### 2. Service points
A service point is a business entity, not a building.

Suggested fields:
- service_point_id
- service_point_name
- business_entity_id
- business_entity_name
- service_point_type
- service_point_status
- region
- business_unit
- operating_unit
- opening_date
- planned_closure_date
- source_system
- source_record_id
- effective_date

### 3. Occupancies
Associative entity between a service point and a building over time. This is essential for multi-occupant buildings and relocations.

Suggested fields:
- occupancy_id
- building_id
- service_point_id
- occupancy_type: owner_occupant / tenant / subtenant / shared
- occupancy_status
- occupied_area_sqft
- floor_numbers
- space_description
- occupancy_start_date
- occupancy_end_date
- is_primary_location
- is_current
- lease_id if applicable
- source_system
- source_record_id

### 4. Deficiencies / FCA observations
Primary work-generation source.

Suggested fields:
- deficiency_id
- building_id
- component_id if known
- title
- observation
- description
- proposed_corrective_action
- action_type: maintenance / repair / replacement / investigation / other
- uniformat_level_1
- uniformat_level_2
- uniformat_level_3
- uniformat_level_4
- uniformat_code
- uniformat_description
- condition_rating: good / fair / poor / very_poor
- priority_rating
- risk_rating
- intervention_horizon
- recommended_intervention_year
- quantity
- unit_of_measure
- unit_cost
- source_total_cost
- cost_date
- cost_source
- location
- floor
- room_or_zone
- inspection_date
- inspector_reference
- photo_reference
- document_reference
- status
- source_system
- source_record_id

Keep `observation` separate from `proposed_corrective_action`: the inspector's proposed corrective action is evidence/input, not automatically the final investment decision.

### 5. Components / asset register
Suggested fields:
- component_id
- building_id
- component_name
- component_type
- system_name
- uniformat_code
- uniformat_level_3
- uniformat_level_4
- manufacturer
- model
- serial_number
- location
- floor
- zone
- installation_year
- installation_date
- last_major_replacement_year
- expected_useful_life_years
- remaining_useful_life_years
- expected_end_of_life_year
- condition_rating
- criticality_rating
- quantity
- unit_of_measure
- replacement_value
- replacement_value_date
- maintenance_strategy
- status
- source_system
- source_record_id

### 6. Universal accessibility
Preferred scalable model: one record per assessed criterion, not one permanent column per criterion.

Suggested fields:
- accessibility_assessment_id
- building_id
- assessment_date
- criterion_id
- criterion_category
- criterion_description
- compliance_status: compliant / non_compliant / not_applicable / unknown
- observation
- recommended_action
- priority
- estimated_cost
- evidence_reference
- source_system
- source_record_id

Never collapse `unknown` into `non_compliant`.

### 7. Future initiatives
Use `initiative` for known future business/real-estate interventions so it is not confused with Agent A's generated opportunities.

Suggested fields:
- initiative_id
- building_id
- service_point_id if business-driven
- initiative_name
- initiative_description
- initiative_type
- business_driver
- strategic_driver
- planned_scope
- planned_start_year
- planned_completion_year
- estimated_cost
- cost_date
- initiative_status
- approval_status
- dependency
- constraint
- source_system
- source_record_id

### 8. Projects
Suggested fields:
- project_id
- building_id
- service_point_id if relevant
- project_name
- project_description
- project_type
- project_status
- project_phase
- approved_scope
- planned_start_date
- planned_completion_date
- actual_start_date
- actual_completion_date
- approved_budget
- forecast_cost
- committed_cost
- actual_cost
- project_manager_reference
- affected_uniformat_codes
- affected_component_ids
- related_initiative_id
- source_system
- source_record_id

Projects are checked before new work packages are proposed to reduce duplicate scope.

### 9. Leases
Lease data must preserve the distinction between physical building and occupying business entity.

Suggested fields:
- lease_id
- building_id
- service_point_id
- occupancy_id
- lease_type
- lease_status
- landlord_reference
- tenant_reference
- leased_area_sqft
- lease_start_date
- lease_end_date
- renewal_option_date
- renewal_option_end_date
- notice_date
- remaining_term_months
- annual_base_rent
- operating_cost
- total_occupancy_cost
- renewal_option
- termination_option
- planned_exit
- planned_exit_date
- source_system
- source_record_id

A lease-end trigger flows through `lease -> occupancy -> service point -> building`, never through building alone.

## Strategic/enrichment domains

### 10. Asset strategy / finance
Suggested fields:
- building_id
- detention_horizon_years
- ownership_strategy
- planned_disposition_date
- planned_acquisition
- planned_exit
- strategic_importance
- investment_posture
- capital_constraint
- strategy_effective_date
- strategy_version

This is the preferred location for deterministic strategy bands such as `<2 years`, `2-5 years`, and `>5 years`.

### 11. Portfolio risk / compliance
Suggested fields: `risk_id`, `building_id`, `risk_type`, `risk_category`, `probability`, `impact`, `risk_score`, `regulatory_requirement`, `compliance_status`, `required_action`, `target_date`, `source_system`.

### 12. Energy / carbon / building performance
Examples: energy use intensity, utility consumption, emissions, carbon targets and building performance indicators.

### 13. Maintenance / CMMS history
Work orders, recurring failures, preventive maintenance, breakdown frequency, asset downtime and maintenance cost history.

### 14. Space / utilization
Area by occupant, vacancy, utilization, capacity and consolidation opportunities.

### 15. BIM / spatial / GIS references
Model identifiers, floor/space IDs, coordinates, geometry references, 360 imagery and other spatial evidence.

## Association hierarchy
1. Exact authoritative ID.
2. Approved crosswalk table.
3. Composite deterministic key explicitly documented.
4. Fuzzy matching only as a flagged exception requiring human validation.

Never silently join using only building name or street address.

## Canonical Site Context
Before Agent A runs, deterministic code should assemble one `site_context.json` for the selected building. It contains the building record and only the related service points, occupancies, deficiencies, components, accessibility assessments, initiatives, projects, leases, strategy and available enrichment domains.

The Site Context Builder must preserve IDs and source lineage. It must not flatten multi-occupant relationships into one ambiguous building-level record.

## V0.2 pipeline run
Each execution creates a `pipeline_run.json` containing run ID, building scope, source snapshots, data-quality results, association exceptions, rule versions, prompt/agent versions, stage states, artifact paths, human approvals, timestamps and unresolved exceptions.

The run manifest is the auditable spine of the pipeline.