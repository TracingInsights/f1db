# Lap leaders 1950–1981

Who led every lap of every World Championship race from 1950 to 1981, as **stints** (one row per uninterrupted spell in the lead). F1DB has per-lap positions only from 1982 (via lap times), so this fills the earlier years.

**Licence:** CC BY-SA 4.0, extracted from the English Wikipedia templates `Template:F1Laps<year>` (Wikipedia contributors). See `../README.md`.

## `lap-leaders.csv`

| Column | Meaning |
| --- | --- |
| `raceId` | F1DB race id (`race.yml` `id`) |
| `year`, `round`, `grandPrixId` | F1DB race keys |
| `driverId` | F1DB driver id of the leader |
| `firstLap`, `lastLap` | first and last lap of the stint (inclusive) |
| `laps` | `lastLap − firstLap + 1` |
| `source` | `wikipedia` |
| `sourcePage`, `sourceRevision` | template title and the exact revision read |
| `sourceKey` | race key inside the template (e.g. `RSA`) |

357 races, 1,366 stints, 111 different leaders.

## Validation (see `VALIDATION.md`)

Every race must pass, or it is left out:

1. Stints cover laps 1 … F1DB race laps with no gap or overlap.
2. The template's lap count equals F1DB `race.yml` `laps`.
3. Every leader is an entrant in F1DB's race results for that race.
4. The last stint belongs to the classified winner, or to a driver F1DB shows as disqualified or penalised after the race (1976 Britain, 1978 Italy, 1980 Canada are the pre-1982 cases). Shared cars (e.g. 1951 France) count every driver F1DB classifies first.

Where a bar and its caption disagree (1959 Netherlands, Bonnier), the plotted bar is used and the difference is noted.

**Accuracy check.** The same templates exist for 1982 onward, where F1DB-derived lap times give the leader of every lap. On 810 races and 50,135 laps the templates name the same leader on **99.84 %** of laps (799 races identical on every lap). The pre-1982 data comes from the same templates and passes the same structural checks.

All 357 races from 1950 to 1981 pass.
