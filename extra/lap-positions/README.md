# Lap-by-lap positions — every Grand Prix and sprint

Running order at the end of every lap of 1,156 World Championship Grands Prix (1950 – 2026 São Paulo) and 30 sprints,
1,260,220 rows. Compiled on 2026-11-13 from published per-race lap charts, resolved to F1DB ids and validated against
F1DB, published laps-led tables, the official timing lap data (1982 onward), Wikipedia and oldracingcars.com — see
[`VALIDATION.md`](VALIDATION.md).

The same data is in the F1DB source as `src/data/seasons/<year>/races/<race>/lap-positions.yml` and
`sprint-lap-positions.yml` (built into `f1db-races-lap-positions` / `f1db-races-sprint-lap-positions`).

**Licence note:** compiled from third-party published race records, not CC BY. Do not upstream it to F1DB or relicense
it without the owner's decision.

## `lap-positions.csv`

| Column | Meaning |
| --- | --- |
| `raceId` | F1DB race id (`race.yml` `id`) |
| `year`, `round` | season and F1DB round |
| `sprint` | `false` = Grand Prix, `true` = sprint |
| `lap` | lap number; `0` = starting order |
| `position` | running position at the end of that lap, 1..n with no gaps |
| `driverId` | F1DB driver id |
| `driverNumber` | the car's number as in F1DB race (or sprint) results — keeps shared drives unambiguous |

Sorted by year, round, sprint, lap, position. (`raceId`, `sprint`, `lap`, `position`) and (`raceId`, `sprint`, `lap`,
`driverNumber`) are unique.

## What the rows mean

- **Lap n** lists every car that completed n laps, in on-track order at the line. A car leaves the chart after its last
  completed lap. Post-race time penalties are not applied.
- **Lap 0** is the starting order of the cars that started. It differs from F1DB `starting-grid-positions` in 37 races
  (pit-lane starters, grid penalties, 1984 Tyrrell …), all listed in `VALIDATION.md`.
- **Red-flag stoppages:** interruption rows are dropped; lap numbers run on across the stoppage. 1959 Germany (two heats
  at AVUS) is one 60-lap sequence.
- **Shared drives (1950s–60s):** the driver at the wheel is named; when a driver took over another car he moves to that
  car's `driverNumber`, so a driver can appear twice in one lap number (one row per car).
- **2014 China** was classified after 54 of the 56 laps run: laps after the official distance are dropped.

## Not included

The Indianapolis 500 rounds 1950–1960 (no lap chart published) and 1967 Germany (the chart covers only the Formula 1 cars
of a mixed F1/F2 field).
