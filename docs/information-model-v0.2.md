# Information Model — Current Canonical View

> The filename is retained from the original V0.2 information-model milestone. The content below reflects the current V0.3 canonical conventions. For normative precedence, read `docs/CANONICAL-CONVENTIONS.md` first.

This document defines the reference information model for a building-level investment-planning pipeline. It intentionally contains no confidential operational data.

## Core principles

1. Treat each source as a domain connected through explicit identifiers and temporal relationships rather than as independent spreadsheets.
2. The physical **building/premises** is the atomic analysis unit and uses `building_id`.
3. A logical `site_id`, a business transit/service point, and a physical building are distinct concepts.
4. A transit/service point can move over time. Current/historical physical location is resolved through `occupancy` relationships.
5. A site can contain multiple transits and can contain owned and leased portions simultaneously.
6. Source identifiers are preserved through mappings/crosswalks; LLMs do not invent authoritative identity associations.

## Canonical identity entities

Primary identity entities include:

- `region_id`
- `branch_id`
- `site_id`
- `building_id`
- `service_point_id`
- source `transit_id` / transit number where applicable
- `occupancy_id`
- `lease_id`
- optional `premises_id` / building-portion identifier when mixed-tenure data requires it

Work-generation and planning entities include:

- `deficiency_id`
- `component_id`
- `accessibility_assessment_id`
- `initiative_id`
- `project_id`
- `strategic_context_id`

See `docs/identity-and-occupancy-model.md` for the temporal identity model.

## Canonical terminology

Use **detention horizon / horizon de détention** throughout the model.

Canonical field:

`detention_horizon_years`

Do not use `retention_horizon`.

Canonical bands:

- `LT_2_YEARS`
- `2_TO_5_YEARS`
- `GT_5_YEARS`
- `UNKNOWN`

---

# Source domains

## 1. Region / Branch / Site hierarchy

These fields support user filtering and organizational/location scope. They do not replace physical or business identities.

Suggested fields:

- region_id
- region_name
- branch_id
- branch_name
- site_id
- site_name
- site_status
- source_system
- source_record_id
- effective_date

A site may contain multiple buildings/premises and multiple transits/service points.

## 2. Buildings / physical premises

One record per stable physical building/premises analysis unit.

Suggested fields:

- building_id
- site_id
- building_name
- building_status
- building_type
- address
- municipality
- province
- postal_code
- latitude
- longitude
- construction_year
- major_renovation_year
- gross_area_sqft
- number_of_floors
- number_of_basements
- replacement_cost_per_sqft
- authoritative_replacement_value if available
- replacement_value_date
- flood_risk_rating
- overall_risk_rating
- fci
- bfi
- condition_rating
- source_system
- source_record_id
- effective_date

Replacement value may be deterministically calculated as `gross_area_sqft * replacement_cost_per_sqft` when an authoritative value is not supplied and the applicable rule authorizes the calculation.

Do not rely on a site-level tenure field when the site can contain mixed owned/leased portions.

## 3. Service points / transits

A service point/transit is a business identity, not a building.

Suggested fields:

- service_point_id
- transit_id / transit_number when applicable
- service_point_name
- business_entity_id
- business_entity_name
- service_point_type
- service_point_status
- business_unit
- operating_unit
- opening_date
- planned_closure_date
- source_system
- source_record_id
- effective_date

Never use a transit number as a permanent `building_id` or `site_id`.

## 4. Occupancies

Occupancy is the temporal bridge between a business identity and physical premises.

Suggested fields:

- occupancy_id
- building_id
- site_id
- premises_id if applicable
- service_point_id
- transit_id if needed for source lineage
- occupancy_type
- occupancy_status
- occupied_area_sqft
- floor_numbers
- space_description
- occupancy_start_date
- occupancy_end_date
- is_primary_location
- is_current
- tenure_type if authoritative at this relationship level
- lease_id if applicable
- source_system
- source_record_id

A transit's movement between buildings must be represented as dated occupancy records, not by overwriting history.

## 5. Premises / building portions — optional extension

Use this explicit layer only when real-data onboarding demonstrates that mixed tenure or physical subdivision cannot be represented accurately through building + occupancy + lease relationships alone.

Suggested fields:

- premises_id
- site_id
- building_id
- premises_name
- tenure_type: owned / leased / other
- area_sqft
- floor_numbers
- valid_from
- valid_to
- source_system
- source_record_id

## 6. Deficiencies / FCA observations

Primary work-generation source.

Suggested fields:

- deficiency_id
- building_id
- premises_id if applicable
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

Keep `observation` separate from `proposed_corrective_action`. The inspector's corrective action is source evidence, not automatically the final investment decision.

## 7. Components / asset register

Suggested fields:

- component_id
- building_id
- premises_id if applicable
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

Useful life is planning evidence, not a deterministic failure date.

## 8. Universal accessibility

Preferred scalable model: one record per assessed criterion.

Suggested fields:

- accessibility_assessment_id
- building_id
- premises_id if applicable
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

Never collapse `unknown` into `non_compliant` or `compliant`.

## 9. Future initiatives

Use `initiative` for known future business/real-estate interventions so it is not confused with Agent A's generated opportunities.

Suggested fields:

- initiative_id
- building_id when physically scoped
- site_id when site scoped
- service_point_id when business driven
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

## 10. Projects

Suggested fields:

- project_id
- building_id when physically scoped
- site_id when site scoped
- service_point_id when business driven
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

Projects are checked before new work packages are recommended to reduce duplicate scope, but they do not erase underlying deficiencies/opportunities.

## 11. Leases

Lease data must preserve the distinction between physical premises and business occupancy.

Suggested fields:

- lease_id
- site_id
- building_id
- premises_id if applicable
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

A lease-end trigger flows through the applicable lease/occupancy/premises/service-point relationship. It must never be interpreted as automatically applying to the entire site or building.

---

# Strategic / enrichment domains

## 12. Asset strategy / finance

Suggested fields:

- building_id or clearly declared strategy scope
- detention_horizon_years
- ownership_strategy
- planned_disposition_date
- planned_acquisition
- planned_exit
- strategic_importance
- investment_posture
- capital_constraint
- fci
- bfi
- amortization_percent where applicable
- strategy_effective_date
- strategy_version

## 13. Strategic context

Optional, high-value qualitative evidence from structured transcription or other authorized contextual sources.

Suggested fields:

- strategic_context_id
- building_id and/or service_point_id according to scope
- source_type
- structured_summary
- strategic_intent
- business_needs
- known_constraints
- known_dependencies
- stakeholder_priorities
- future_changes
- uncertainties
- assumptions
- decision_signals
- confidence
- human_validation_status
- source_reference
- source_system
- source_record_id

Strategic context may influence Agent T reasoning but never silently overwrite authoritative structured facts.

## 14. Risk / compliance

Examples:

- risk_id
- building_id
- risk_type
- risk_category
- probability
- impact
- risk_score
- regulatory_requirement
- compliance_status
- required_action
- target_date
- source_system

## 15. Energy / carbon / building performance

Examples include energy use intensity, utility consumption, emissions, carbon targets and building-performance indicators.

## 16. Maintenance / CMMS history

Work orders, recurring failures, preventive maintenance, breakdown frequency, downtime and maintenance-cost history.

## 17. Space / utilization

Area by occupant, vacancy, utilization, capacity and consolidation opportunities.

## 18. BIM / spatial / GIS references

Model identifiers, floor/space IDs, coordinates, geometry references, 360 imagery and other spatial evidence.

---

# Association hierarchy

Use this preference for authoritative associations:

1. exact authoritative ID;
2. approved crosswalk table;
3. documented deterministic composite key;
4. fuzzy/name/address matching only as a flagged exception requiring explicit human validation.

Never silently join using only building name, transit label or street address.

# Canonical Site Context

Before Agent A runs, deterministic code assembles one `site_context.json` for the selected physical `building_id`.

It contains the building record and only the related service points/transits, temporal occupancies, deficiencies, components, accessibility assessments, initiatives, projects, applicable leases, strategy, strategic context and enabled enrichment domains.

The Site Context Builder must preserve identifiers, effective dates and source lineage. It must not flatten multioccupant, historical transit movement or mixed-tenure relationships into one ambiguous building-level value.

# Stage artifacts

Current agent-stage artifacts use:

- required top-level `building_id`;
- optional parent `site_id`;
- canonical `stage` field.

Do not use legacy examples where `site_id` contains a building ID or `pipeline_state` replaces `stage`.

# Pipeline run

One `pipeline_run.json` represents one building analysis run. A multi-building cockpit selection creates multiple independent runs linked by an optional batch identifier.

The run record can contain run ID, building ID, analysis-manifest ID, source snapshots, mapping versions, data-quality results, association exceptions, rule versions, agent/model versions, stage states, artifact paths, human approvals, timestamps and unresolved exceptions.

The run manifest is the auditable spine of the building pipeline.