# iota-report

A portable, machine-readable format for a **single asteroid-occultation observation report** —
the modern replacement for the IOTA North America Excel report form
(`NorthAmerica_AstReportForm_V5.6.12r.xlsx`).

`iota-report` gives the occultation community one shared contract for exchanging a reduced
observation:

- **Pydantic v2 models** (Python) that define and validate the report.
- A faithful port of the Excel form's **timing-correction engine** — camera integration delay,
  VTI offset, and RunCam rolling-shutter corrections — with the spreadsheet's *silent*
  correction-withholding turned into **explicit, typed errors**.
- A committed, versioned **canonical JSON Schema** (draft 2020-12): the language-agnostic wire
  contract.
- **Generated TypeScript and C# types** produced from that schema, so .NET tools (Occult,
  Occult Watcher, Tangra, SharpCap) and web tools (Occult Watcher Cloud, IOTA Hub) can consume a
  report without a Python toolchain.

No Excel file is ever produced or required. A report is a JSON document.

## Who this is for

If you write occultation software — a capture/reduction tool, a coordination platform, or an
archive importer — and you want to **emit or ingest a structured observation report**, this
package is the shared definition. Python users get the models and correction engine directly;
other languages consume the JSON Schema and the generated types.

## Install (Python)

The package is not on PyPI (yet). Install from Git:

```bash
uv add "iota-report @ git+https://github.com/skycarl/iota-report@v0.1.0"
# or:  pip install "iota-report @ git+https://github.com/skycarl/iota-report@v0.1.0"
```

## Quickstart (Python)

```python
from iota_report import (
    Report, apply_corrections, check_compatibility, parse_latitude,
)

# Build (or model_validate from JSON) a report:
report = Report.model_validate(report_dict)

# Validate the equipment configuration before trusting a correction:
issues = check_compatibility(
    report.camera.camera_model,
    report.camera.exposure,
    report.timing_setup.ote_program,
    report.camera.video_format,
)
for issue in issues:
    print(issue.kind, issue.message)

# Compute corrected D/R times (pure -- does not mutate `report`):
result = apply_corrections(report)            # raises IncompatibleConfigurationError if invalid
report.timings.corrected = result.corrected   # embed the computed block
print(result.corrected.disappearance_utc, result.corrected.total_correction_d_s)

# Parse a legacy coordinate string to signed decimal degrees:
lat = parse_latitude("37 30 00.00", "N")      # -> 37.5
```

Serialize the finished report:

```python
report.timings.corrected = apply_corrections(report).corrected
json_text = report.model_dump_json(indent=2)  # times are Z-suffixed, millisecond precision
```

### The correction engine

The engine is the reason the Excel form existed. It turns the **raw** D/R times an observer reads
off the VTI into **corrected** times, per the documented tables and formulas:

- `apply_corrections(report)` -- the one entry point. Returns corrected times plus the per-edge
  component breakdown (camera delay, VTI offset, total) and a `near_midnight_review` flag.
  Self-correcting cameras, manual mode, and blank OTE pass the entered times through unchanged.
- `camera_delay(...)`, `vti_offset(...)`, `rolling_shutter_correction(...)` -- the component
  functions, exposed for previews and testing.
- `check_compatibility(...)` returns a list of typed `CompatibilityIssue`s; an out-of-matrix
  configuration raises `IncompatibleConfigurationError` (it no longer *silently* drops the
  correction, as the spreadsheet did).

Full ISO-8601 UTC datetimes are used throughout, which removes the Excel form's midnight-wrap
fragility: an event near 00:00 UT is computed correctly and merely *flagged* for review.

## JSON Schema and generated types

- **Canonical schema:** [`schema/iota-report.schema.json`](schema/iota-report.schema.json)
  (JSON Schema draft 2020-12). This is the source of truth for non-Python consumers.
- **TypeScript:** [`generated/typescript/iota-report.ts`](generated/typescript/iota-report.ts)
- **C#:** [`generated/csharp/IotaReport.cs`](generated/csharp/IotaReport.cs) (Newtonsoft.Json)

The types are generated from the schema with [quicktype](https://quicktype.io) and committed. CI
regenerates both and fails on drift, so the committed artifacts always match the models. To
regenerate locally:

```bash
uv run python scripts/export_schema.py      # models  -> schema/iota-report.schema.json
./scripts/generate_types.sh                 # schema  -> generated/{typescript,csharp}
```

## Schema versioning policy

`SCHEMA_VERSION` (semantic version, currently `1.0.0`) is the version of the **schema** -- the wire
contract -- and is embedded in the schema's `$id`. It is distinct from the **package** version in
`pyproject.toml`:

- **Package patch** bump: correction-table or engine fixes that don't change the wire shape.
- **Schema minor** bump: additive, optional fields (backward-compatible).
- **Schema major** bump: any breaking change. Consumers should validate the `schema_version`
  major of a report they receive.

Git tags are `v<package_version>`; downstream consumers (e.g. IOTA Hub) pin a tag.

## Mapping to PDS `occtimings`

The PDS Small Bodies Node "Asteroid Occultations" bundle (`occtimings`, maintained by Dave Herald)
is the canonical archival sink for reduced observations. `iota-report` is designed so its archival
fields map losslessly onto the per-observer `occtimings` record:

| PDS `occtimings` field (per-observer record) | `iota-report` field |
|---|---|
| Observer name(s) | `observer.names` |
| Site latitude | `station.latitude_deg` (signed decimal degrees) |
| Site longitude | `station.longitude_deg` (signed decimal degrees) |
| Site elevation | `station.elevation_m` (metres, MSL) |
| Geodetic datum | `station.datum` (default WGS84) |
| Telescope aperture | `telescope.aperture_cm` |
| Timing method | `timing_setup.method` |
| Positive / negative flag | `result` (`POSITIVE` / `NEGATIVE` / `UNSURE`) |
| Disappearance (D) time | `timings.corrected.disappearance_utc` |
| Reappearance (R) time | `timings.corrected.reappearance_utc` |
| D/R uncertainties | `timings.disappearance.error_bars` / `timings.reappearance.error_bars` (0.6827 / 0.9500 / 0.9973 CL) |
| Target asteroid number / name | `event.asteroid_number` / `event.asteroid_name` |
| Occulted star (catalog + id) | `event.star_catalog` / `event.star_number` |

Object and star identity conventions follow Occult prediction XML (asteroid number + name +
optional provisional designation; catalog-formatted star number; WGS84 default) so a report joins
cleanly to the prediction it came from. This mapping is documentation only -- there is no separate
PDS model in the package.

## Development

```bash
uv sync
uv run pytest                 # tests, including golden correction vectors
uv run ruff check .           # lint
uv run ruff format --check .  # format
uvx ty check                  # type check
```

Golden correction vectors live in `tests/golden/corrections.json`; every expected number is
transcribed from the Excel form's documented tables/formulas, so the tests pin the engine to the
spreadsheet's own values.

## License

MIT -- see [LICENSE](LICENSE).
