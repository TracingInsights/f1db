# Data review of `src/data` (2026-11-13)

Every completed race 1950–2026 (1,169 Grands Prix, 30 sprints) was compared field by field with published per-race
records — entry lists, qualifying, starting grids, results, best laps, laps led, lap charts, championship tables — and
with driver, constructor, engine, circuit and season records. F1DB was completed where those records had facts it lacked
or got wrong.

## Rules every change followed

- A **conflict** was changed only when an independent source confirmed the new value — formula1.com archive,
  Jolpica/Ergast, contemporary *Motor Sport* reports, FlyingLap, oldracingcars, FIA documents, or Wikipedia where its
  table is independently sourced. Otherwise F1DB was kept and the case recorded as unresolved.
- A **gap** (empty field / missing row) was filled after consistency checks and sampled third-source checks.
- Wording was not rewritten (e.g. retirement reasons); only blank reasons were filled, in F1DB's vocabulary.
- Derived values were recomputed, not copied: gaps and intervals from times, positions after inserting rows.
- A final pass made every race-level file name the same car (constructor / engine / tyre) for a driver, kept
  `starting-grid-positions.yml` and `race-results.yml` `gridPosition` in step (F1DB's 1984 convention of leaving the
  excluded Tyrrells off the grid is kept) and added the tyre makers those cars used to `entrants.yml`. Against the
  upstream baseline: no new cross-file mismatch; 18 grid and 2 entrant mismatches that upstream had are resolved.

## Changes by area (about 7,000 field-level changes)

| Area | F1DB files | Changes |
| --- | --- | --- |
| Best laps | `fastest-laps.yml` | every driver's best race lap added where a full list exists (4,509 rows); lap / tyre fixes |
| Race results | `race-results.yml`, `sprint-race-results.yml` | 811 — laps, times, gaps, statuses, blank retirement reasons, relief drivers |
| Qualifying | `qualifying*.yml`, `pre-qualifying-results.yml` | 519 — times, positions, 31 missing rows |
| Starting grids | `starting-grid-positions.yml`, `sprint-starting-grid-positions.yml` | 201 — positions, times, pit-lane starts, grid penalties |
| Race metadata | `race.yml`, `circuits/`, `grands-prix/` | 146 — dates, laps, distances, layouts |
| Entries | `seasons/*/entrants.yml`, entity files | 115 — entrants, chassis, engines, tyres per round |
| Drivers | `drivers/` | 54 — birth / death dates and places, names |
| Standings | `*-standings.yml` | 49 — positions, points, ties |
| Consistency pass | all race-level files, `entrants.yml` | 199 — see above |

## New F1DB data types (schema + build)

| File (per race) | Content | Output |
| --- | --- | --- |
| `lap-positions.yml` | running order at the end of every lap (lap 0 = start): `- lap: n` / `drivers: [driverId, …]`, `"<number>:<driverId>"` when a driver had two cars | `f1db-races-lap-positions`, SQL view `lap_position` |
| `sprint-lap-positions.yml` | the same for sprint races | `f1db-races-sprint-lap-positions`, view `sprint_lap_position` |
| `sprint-fastest-laps.yml` | every driver's best sprint lap (same shape as `fastest-laps.yml`) | `f1db-races-sprint-fastest-laps`, view `sprint_fastest_lap` |

1,156 race and 30 sprint lap charts (≈1.25 M rows) and 30 sprint best-lap lists. Schema:
`src/schema/current/single/f1db.schema.json` (`LapPosition`; `Race.lapPositions`, `sprintFastestLaps`,
`sprintLapPositions`) and `src/schema/current/splitted/f1db-races-lap-positions.schema.json`. Build: the reader's
`readLapPositions` expands the compact rows and takes number / constructor / engine / tyre from the matching result row;
mappers, CSV / JSON / Smile / SQL / SQLite writers; `race_data.lap_position_lap` and three views in `create_schema.sql`.
`gradle.properties` gives Gradle 4 GB (`-Xmx4g`), which the lap positions need. Known gap: the 1965 British GP chart
stops at lap 78 of 80.

## Validation

`./gradlew build -x test` passes. The F1DB test suite (`./gradlew test`, needs Docker) was not run.

## Licence

Facts compiled from third-party published race records and the sources named above. Decide before contributing any of
this upstream to F1DB (CC BY 4.0).
