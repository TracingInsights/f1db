# Extra datasets (TracingInsights fork)

Datasets compiled on top of F1DB that are **not part of the upstream F1DB build** and are licensed differently from it.

| Folder | Contents | Rows | Licence |
| --- | --- | --- | --- |
| `lap-leaders/` | Lap-leader stints for every World Championship race 1950–1981 (357 races) | 1,366 stints | CC BY-SA 4.0 |
| `non-start-reasons/` | Reasons for F1DB non-start rows (DNS / DNP / EX / DSQ) that have no `reasonRetired` | 20 of 83 | CC BY-SA 4.0 |

## Licence and attribution

Both datasets are extracted from English Wikipedia and are therefore **CC BY-SA 4.0** (<https://creativecommons.org/licenses/by-sa/4.0/>), attributed to the Wikipedia contributors of the pages named in each row (`sourcePage`, `sourceRevision`). Because of the ShareAlike term they must **not** be merged into upstream F1DB (CC BY 4.0) and must keep this licence when redistributed.

Wikipedia's lap-leader templates cite other statistics sites as references; using them was an explicit owner decision on 2026-11-05.

## Rebuild

Each folder has a `tools/` directory and a `VALIDATION.md` describing every check. Downloads go to a directory outside the repository; only extracted facts and revision ids are committed.

```sh
# lap leaders
mkdir -p /tmp/wp-f1laps-raw
python3 -I extra/lap-leaders/tools/fetch_templates.py /tmp/wp-f1laps-raw 1950 2026
python3 -I extra/lap-leaders/tools/compile.py /tmp/wp-f1laps-raw . extra/lap-leaders [path/to/f1db-races-lap-times.csv]

# non-start reasons
python3 -I extra/non-start-reasons/tools/find_missing.py . > /tmp/nonstart-missing.json
mkdir -p /tmp/wp-races-raw
python3 -I extra/non-start-reasons/tools/fetch_race_pages.py /tmp/nonstart-missing.json . /tmp/wp-races-raw
python3 -I extra/non-start-reasons/tools/compile.py /tmp/nonstart-missing.json /tmp/wp-races-raw . extra/non-start-reasons
```

Requires Python 3 and PyYAML.

## Complete lap data (2026-11-13)

Compiled from published per-race race records and validated against F1DB and independent sources (official timing lap
data, Wikipedia, contemporary reports). **Licence note:** not CC BY — do not upstream to F1DB or relicense without the
owner's decision.

| Folder | Contents | Rows |
| --- | --- | --- |
| `lap-leaders-all/` | Lap-leader stints for every completed Grand Prix (1,169, 1950–2026) and sprint (30) | 4,406 stints |
| `lap-positions/` | Running order at the end of every lap (lap 0 = start) for 1,156 Grands Prix and 30 sprints, with car numbers | 1,260,220 rows |
| `data-audit-2026-11/` | Summary of the 2026-11-13 data review of `src/data` and the new lap-position data types | — |

Each folder has its own `README.md` (and `VALIDATION.md` for the datasets).
