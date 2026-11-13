# Lap-by-lap positions — validation (2026-11-13)

## Coverage

- 1,260,220 rows: 1,156 Grands Prix + 30 sprints. Races without a chart: the 11 Indianapolis 500 rounds 1950–1960.
  Excluded: 1967 Germany (Formula 1 cars only in a mixed F1/F2 race).

## Integrity

- (raceId, sprint, lap, position) unique; positions contiguous 1..n on every lap — **pass**
- every driverId exists in `src/data/drivers`, every raceId exists, year/round match `race.yml` — **pass**
- every (driverId, driverNumber) pair is a row of that race's F1DB (sprint) results — **pass**
- (raceId, sprint, lap, driverNumber) unique — one cell per car per lap — **pass**
- every lap-chart driver code resolved to an F1DB driver — **pass** (26,207 codes); 22 charts whose code legend was
  offset against the codes were relabelled, and a few cells fixed by documented manual overrides.

## Consistency with F1DB

- Chart laps == F1DB race laps: 1,185 / 1,186; exception 1965 Great Britain (chart 78 laps, race 80).
- A driver's last lap in the chart == F1DB `laps` for 1,182 full charts; the differences are shared cars, retirements
  F1DB credits with one more lap, and classified-not-running cars.
- Classified finishers ordered by (laps, last-lap position) vs F1DB classification: 16,177 places agree; 678 differ
  in 160 charts, almost all post-race time penalties.
- Lap 0 vs F1DB `starting-grid-positions` (starters only): 1,149 identical, 37 differ (pit-lane starters placed by
  qualifying slot, grid penalties, 1984 Tyrrell, tie orders).

## Leaders

- Chart P1 vs the published laps-led tables: 73,783 laps compared, differences in 3 charts, each checked against
  official timing or contemporary reports. Cells were overridden only where official timing settles it (e.g. 2026
  Australia lap 8, P1/P2 swapped); 1990 Canada keeps the on-the-road order (Berger), not the corrected-time leader.
- vs the fork's `extra/lap-leaders` (Wikipedia, 1950–1981): 344 races, 339 identical on every lap; 22,885 laps,
  99.94 % same leader.
- vs Wikipedia `Template:F1Laps<year>` 1950–2026: 1,155 races, 1,148 identical; 73,126 laps, 99.90 % same leader.
- vs leaders derived from official timing lap data (1982 onward): 99.95 % of laps identical; every disagreement was
  checked against a contemporary report (*Motor Sport*) and resolved per lap.
