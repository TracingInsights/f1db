# Lap leaders — every Grand Prix and sprint

Who led every lap of every World Championship Grand Prix and sprint, as **stints** (one row per uninterrupted spell in
the lead): 1,169 Grands Prix (1950 – 2026 round 20) and 30 sprints, 4,406 stints, 183 different leaders.

Compiled on 2026-11-13 from published per-race laps-led tables, validated against the same races' lap charts
(`../lap-positions/`), the fork's Wikipedia-based `../lap-leaders/` (1950–1981), leaders derived from official timing lap
data (1982 onward) and contemporary race reports — see [`VALIDATION.md`](VALIDATION.md).

**Licence note:** compiled from third-party published race records, not CC BY. Do not upstream it to F1DB or relicense
it without the owner's decision.

## `lap-leaders.csv`

| Column | Meaning |
| --- | --- |
| `raceId` | F1DB race id (`race.yml` `id`) |
| `year`, `round` | F1DB race keys |
| `sprint` | `0` = Grand Prix, `1` = sprint race |
| `driverId` | F1DB driver id of the leader (for shared cars, the driver at the wheel) |
| `fromLap`, `toLap` | first and last lap of the stint (inclusive) |
| `laps` | `toLap − fromLap + 1` |

Sorted by `raceId`, `sprint`, `fromLap`. For the Indianapolis 500 rounds (1950–1960) the laps-led table is used without
a lap chart to cross-check.
