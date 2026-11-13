# Non-start reasons

Reasons for F1DB race-result rows with status **DNS, DNP, EX or DSQ** whose `reasonRetired` is empty. F1DB already records a reason for most such rows (DNS 312 of 381, DSQ 156 of 161, EX 8 of 15); this dataset targets the remaining **83** (85 before the corrections on branch `fix/minardi-1985-1986-start-status`, which turned two 0-lap "DNS" rows into first-lap retirements). DNQ / DNPQ are excluded: the status is the reason.

**Licence:** CC BY-SA 4.0, extracted from English Wikipedia race articles (Wikipedia contributors). See `../README.md`.

## `non-start-reasons.csv`

| Column | Meaning |
| --- | --- |
| `raceId`, `year`, `round`, `grandPrixId`, `driverId` | F1DB keys |
| `status` | F1DB status |
| `reason` | the reason as given in the article's classification table |
| `wikipediaStatus` | the status shown in that row (differs from F1DB in 1 row — see below) |
| `source`, `sourcePage`, `sourceRevision` | article and the exact revision read |

## Result

- **20 of 83** rows have a specific reason in Wikipedia.
- The other 63 are listed in `VALIDATION.md`: the article either has no row for the driver, or only restates the status ("Non starter", "Did not start", "Disqualified", "Excluded"). Those rows stay unknown; they need another source.
- 1980 Netherlands, Jochen Mass: Wikipedia says withdrawn (WD), F1DB says DNS. Checked against period sources (2026-11-05): he pulled out during the meeting, unfit after his Austria injury; DNS stands.
- Checked and corrected in F1DB data (branch `fix/minardi-1985-1986-start-status`): 1985 Italy Martini and 1986 San Marino Nannini started and retired on the opening lap (Motor Sport, October 1985 and June 1986 race reports; grandprix.com; Wikipedia), and 1986 Spain Nannini did not start (Motor Sport, Wikipedia, Formula One History).
