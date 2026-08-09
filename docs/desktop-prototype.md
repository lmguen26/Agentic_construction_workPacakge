# Desktop Prototype

V0.3 includes a simple Tkinter desktop application that exposes the deterministic pipeline before live agent execution.

## Run

From the repository root:

```bash
python app/main.py
```

The application loads the synthetic portfolio by default and provides three actions for the selected building:

1. **Validate site** — runs the deterministic Data Quality Gate.
2. **Build site context** — creates the canonical per-building `site_context.json` under `data/outputs/`.
3. **Generate HTML datasheet** — creates and opens a standalone HTML building datasheet under `data/outputs/`.

## Standalone validation

```bash
python scripts/validate_site.py BLDG-001
```

Optional:

```bash
python scripts/validate_site.py BLDG-001 --portfolio path/to/portfolio.json --output data/outputs/BLDG-001.validation.json
```

A blocked site returns process exit code `2`, allowing the validator to be used in scripts or future orchestration.

## Intended corporate integration

The Tkinter app should eventually load canonicalized local data rather than raw operational sources. Source-specific adapters and mappings remain upstream:

```text
raw operational data
  -> source mappings/crosswalks
  -> canonical portfolio datasets
  -> Tkinter site selector
  -> Data Quality Gate
  -> site_context.json
  -> HTML datasheet
  -> Agent A and downstream stages
```

## HTML building datasheet

The generator is deterministic and located at:

`src/spa/building_datasheet.py`

It renders:
- building identity and core metrics
- ownership
- replacement value
- detention horizon/band
- data-quality status
- deficiencies
- components
- accessibility criteria
- service points
- occupancies
- leases
- future initiatives
- current projects
- structured strategic context
- asset strategy
- complete canonical JSON context for audit/debugging

The HTML embeds the canonical site context as JSON and uses lightweight client-side JavaScript only for section filtering. It does not call external services.

## Future integration point

Once Agent A-E outputs are approved, the datasheet can be extended with dedicated sections for:

- normalized opportunities
- clusters
- candidate work packages
- costed work packages
- recommendations
- executive summary
- source-to-recommendation lineage

The HTML layer should display structured artifacts; it should not parse free-form chat transcripts.