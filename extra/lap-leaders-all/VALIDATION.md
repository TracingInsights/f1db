# Lap leaders — validation (2026-11-13)

## Checks (all races)

1. stints cover laps 1 … n with no gap or overlap and agree with each table's per-driver totals;
2. n = F1DB `race.yml` `laps` (sprints: `sprintRaceLaps`), or the classified winner's laps;
3. the last-lap leader is the classified winner, or F1DB shows that driver disqualified / penalised;
4. every leader is an entrant of that race in F1DB;
5. the lap chart (`../lap-positions/`) names the same leader on every lap (shared cars excepted: the chart follows the car).

## Comparison with independent sources

- vs the fork's Wikipedia-based `../lap-leaders/lap-leaders.csv` (1950–1981): 357 races, 355 identical on every lap;
  25,052 laps, 7 with a different leader (99.97 %).
- vs leaders derived from official timing lap data (1982 onward): 812 races, 803 identical; 50,263 laps, 23 different
  (99.95 %).
- Every disagreement, plus spot checks, was checked against a third source (contemporary race reports, mostly
  *Motor Sport*, and official timing): 51 checks — 37 agree, 5 confirm the published laps-led value against the other
  source, 5 explained by convention (e.g. a leader on corrected time vs on the road), 4 unresolved.
- The CSV always keeps the published laps-led value; disagreements are reported, never patched silently.
