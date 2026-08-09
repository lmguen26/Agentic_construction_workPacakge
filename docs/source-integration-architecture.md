# Source Integration Architecture

## Purpose
Keep operational source schemas unchanged while presenting a stable canonical information model to validation, site-context generation, agents, evaluators, and downstream information products.

```text
OPERATIONAL SOURCE DATA
(original columns preserved)
        |
        v
SOURCE ADAPTERS / MAPPINGS
        |
        +-- source field
        +-- canonical field
        +-- transformation
        +-- validation rule
        +-- standards alignment where applicable
        |
        v
CANONICAL INVESTMENT-PLANNING MODEL
        |
        v
DATA QUALITY GATE
        |
        v
site_context.json
        |
        v
A -> B -> C -> T -> E
```

## Three semantic layers

1. **Source layer** — actual operational field names and source-system semantics. Do not rename production sources merely to satisfy the agent pipeline.
2. **Canonical layer** — stable, bounded investment-planning terminology used by all downstream code and agents.
3. **Standards-alignment layer** — optional alignment to OSCRE, Uniformat, ISO-related information requirements, unit standards, or other controlled vocabularies.

The canonical model is the operational contract. Standards alignment is metadata/reference and must not force the pipeline to consume an unnecessarily broad external schema.

## Mapping definitions

Version mappings in Git while keeping production data outside Git.

Recommended structure:

```text
mappings/
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

Each mapping should support:
- source field name
- canonical field name
- required/optional status
- source and canonical data type
- deterministic transformation
- controlled-value crosswalk
- unit conversion if required
- validation rule
- standards alignment if known
- mapping version

Example:

```json
{
  "source": "deficiencies",
  "mapping_version": "0.1",
  "fields": {
    "ID_Def": {
      "canonical": "deficiency_id",
      "required": true,
      "transformation": "direct"
    },
    "ID_Immeuble": {
      "canonical": "building_id",
      "required": true,
      "transformation": "building_id_crosswalk"
    },
    "Code_Uni": {
      "canonical": "uniformat_code",
      "required": false,
      "transformation": "validate_uniformat"
    },
    "Cout_Total": {
      "canonical": "source_total_cost",
      "required": false,
      "canonical_type": "number"
    }
  }
}
```

## Crosswalks

Mappings describe columns; crosswalks resolve identifiers and controlled values.

```text
crosswalks/
  building_ids.json
  service_point_building.json
  condition_rating.json
  intervention_horizon.json
  uniformat.json
  units_of_measure.json
```

Crosswalks must be deterministic and versioned. LLM agents must never invent identifier crosswalks.

## Local data boundary

Production/corporate data should remain outside source control. A local workspace may use:

```text
data/
  raw/
  staging/
  canonical/
  outputs/
```

The entire `data/` directory should be ignored by Git unless a file is explicitly synthetic and approved for version control.

The repository should contain schemas, mappings, crosswalk definitions, rules, agents, prompts, validation code, tests, and synthetic fixtures—not production records.

## Adapter contract

A source adapter performs only deterministic transformations:

```text
source records
   -> field mapping
   -> identifier/value crosswalks
   -> type normalization
   -> unit normalization
   -> validation
   -> canonical records
```

It must produce a transformation report containing:
- source name/version
- mapping version
- input row count
- output row count
- unmapped source fields
- missing required fields
- failed conversions
- unresolved identifiers
- warnings

No LLM is used for authoritative identifier mapping or silent data repair.

## Change isolation

If an operational source renames `Cout_Total` to `Cout_Estime`, update the mapping and tests. The canonical `source_total_cost` field and Agents A-E should remain unchanged.

This isolates source-system change from agent behavior and information-product contracts.

## Standards alignment

Where useful, canonical fields may carry alignment metadata, for example:

```json
{
  "canonical_field": "gross_area_sqft",
  "description": "Gross building area in square feet",
  "source_field": "SUP_BRUTE",
  "standards_alignment": {
    "oscre": null,
    "classification": null
  },
  "unit": "ft2"
}
```

Do not invent an OSCRE mapping. Add alignment only when it has been verified against the relevant standard/model version.

## Recommended first corporate-environment integration

1. Clone the repository into the approved development environment.
2. Create a local integration branch.
3. Keep real data under ignored local paths or approved enterprise storage.
4. Inventory actual source column names without changing the sources.
5. Create mappings and crosswalks for one source at a time.
6. Start with buildings, occupancies/service points, and deficiencies.
7. Generate canonical records for one well-understood building.
8. Run the Data Quality Gate.
9. Generate `site_context.json`.
10. Manually verify that the site context accurately represents the known building facts.
11. Only then execute live Agent A.

The first integration milestone is therefore not an agent response. It is a trusted canonical `site_context.json` generated from real source structures without committing real source data.