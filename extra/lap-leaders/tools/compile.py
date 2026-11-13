#!/usr/bin/env python3
"""Compile lap-leader stints from the Wikipedia F1Laps<year> templates.

Usage:
  python3 -I compile.py <raw-dir> <f1db-root> <out-dir> [lap-times.csv]

  raw-dir       JSON files written by fetch_templates.py ({title, revid, wikitext})
  f1db-root     this repository (reads src/data/seasons and src/data/drivers)
  out-dir       where lap-leaders.csv and VALIDATION.md are written
  lap-times.csv optional f1db-style lap times (raceId, driverId, lap, position)
                used to measure the templates' accuracy for 1982 onward

Every stint is validated against F1DB: stints must cover laps 1..race laps
without gaps or overlaps, the last stint must belong to the race winner, and
every leader must be an entrant of that race. Races that fail any check are
reported and left out of the CSV (nothing is guessed).
"""

import csv
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

import yaml

FIRST_OUTPUT_YEAR = 1950
LAST_OUTPUT_YEAR = 1981  # f1db-derived lap times cover 1982 onward

CASE_RE = re.compile(r'^\|\s*([A-Za-z0-9_ ]+?)\s*=\s*$', re.M)
PERIOD_RE = re.compile(r'Period\s*=\s*from:\s*0\s+till:\s*(\d+)')
STINT_RE = re.compile(
    r'from:\s*(start|\d+)\s+till:\s*(end|\d+).*?text:\s*(.+?)\s*\((Laps?)\s+(\d+)(?:\s*[–-]\s*(\d+))?\)\s*$',
    re.I,
)


def norm(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.replace('ø', 'o').replace('Ø', 'O').replace('ß', 'ss')
    return re.sub(r'[^a-z]', '', text.lower())


def load_drivers(root: str) -> dict:
    drivers = {}
    for path in glob.glob(f'{root}/src/data/drivers/*.yml'):
        with open(path, encoding='utf-8') as fh:
            d = yaml.safe_load(fh)
        drivers[d['id']] = d
    return drivers


def load_races(root: str, year: int) -> list:
    races = []
    for folder in sorted(glob.glob(f'{root}/src/data/seasons/{year}/races/*/')):
        with open(f'{folder}race.yml', encoding='utf-8') as fh:
            race = yaml.safe_load(fh)
        results_path = f'{folder}race-results.yml'
        results = []
        if os.path.exists(results_path):
            with open(results_path, encoding='utf-8') as fh:
                results = yaml.safe_load(fh) or []
        race['results'] = results
        race['folder'] = os.path.basename(folder.rstrip('/'))
        races.append(race)
    races.sort(key=lambda r: r['round'])
    return races


def parse_template(wikitext: str) -> list:
    """Return [(key, period_laps, [(name, first, last, raw_line)])] in page order."""
    cases = []
    marks = list(CASE_RE.finditer(wikitext))
    for i, m in enumerate(marks):
        body = wikitext[m.end() : marks[i + 1].start() if i + 1 < len(marks) else len(wikitext)]
        period = PERIOD_RE.search(body)
        stints = []
        problems = []
        notes = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith('from:'):
                continue
            s = STINT_RE.search(line)
            if not s:
                problems.append(f'unparsed line: {line[:120]}')
                continue
            frm, till, name, _, a, b = s.groups()
            label_first, label_last = int(a), int(b or a)
            # The plotted bar is the data; the label is its caption. When they
            # disagree the bar wins and the difference is reported as a note.
            first = 1 if frm.lower() == 'start' else int(frm) + 1
            is_end = till.lower() == 'end'
            last = label_last if is_end else int(till)
            if (first, last) != (label_first, label_last):
                notes.append(
                    f'label says laps {label_first}–{label_last} for {name.strip()}, bar says {first}–{last}; bar used'
                )
            stints.append((name.strip(), first, last, is_end, line))
        cases.append((m.group(1).strip(), int(period.group(1)) if period else None, stints, problems, notes))
    return cases


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def match_driver(name: str, entrant_ids: list, drivers: dict):
    target = norm(name)
    exact, last_only = [], []
    for did in entrant_ids:
        d = drivers.get(did)
        if not d:
            continue
        names = {norm(d.get('name') or ''), norm(d.get('fullName') or '')}
        names.add(norm(f"{d.get('firstName') or ''}{d.get('lastName') or ''}"))
        if target in names:
            exact.append(did)
        elif norm(d.get('lastName') or '') and target.endswith(norm(d.get('lastName') or '')):
            last_only.append(did)
    if len(set(exact)) == 1:
        return exact[0], 'name'
    if not exact and len(set(last_only)) == 1:
        return last_only[0], 'surname'
    if not exact and not last_only:
        near = [did for did in entrant_ids if did in drivers and edit_distance(target, norm(drivers[did].get('name') or '')) <= 1]
        if len(set(near)) == 1:
            return near[0], 'spelling (one letter apart)'
    return None, f'ambiguous or missing ({sorted(set(exact or last_only))})'


def winners_of(race: dict) -> set:
    """All drivers classified first (shared cars give more than one)."""
    return {r['driverId'] for r in race['results'] if r.get('position') == 1}


def post_race_change(race: dict, driver_id: str):
    """Why the last car to lead on the road is not the classified winner."""
    for r in race['results']:
        if r['driverId'] != driver_id:
            continue
        pos = r.get('position')
        if isinstance(pos, str) and pos.upper() in ('DSQ', 'EX'):
            return f'disqualified ({r.get("reasonRetired") or "no reason recorded"})'
        if r.get('timePenalty'):
            return f'time penalty {r["timePenalty"]}, classified P{pos}'
        if isinstance(pos, int) and pos > 1:
            return f'classified P{pos} after the race'
    return None


def validate(race: dict, period: int, stints: list, drivers: dict):
    """Return (rows, errors, notes)."""
    errors, notes, rows = [], [], []
    laps = race.get('laps')
    entrant_ids = [r['driverId'] for r in race['results']]
    if period is not None and laps is not None and period != laps:
        errors.append(f'template period {period} laps != f1db laps {laps}')
    expected = 1
    for name, first, last, is_end, _ in stints:
        if first != expected:
            errors.append(f'gap/overlap: stint of {name} starts at lap {first}, expected {expected}')
        expected = last + 1
        did, how = match_driver(name, entrant_ids, drivers)
        if not did:
            errors.append(f'driver "{name}" not matched: {how}')
        elif how != 'name':
            notes.append(f'"{name}" matched by {how} to {did}')
        rows.append((did, first, last, name))
    if laps is not None and expected - 1 != laps:
        errors.append(f'stints end at lap {expected - 1}, f1db laps {laps}')
    wins = winners_of(race)
    if rows and wins and rows[-1][0] and rows[-1][0] not in wins:
        why = post_race_change(race, rows[-1][0])
        if why:
            notes.append(f'last leader on the road {rows[-1][0]} is not the classified winner {sorted(wins)}: {why}')
        else:
            errors.append(f'last leader {rows[-1][0]} is not the winner {sorted(wins)}')
    return rows, errors, notes


def align(cases: list, races: list, report: list, year: int) -> list:
    """Template order is the calendar order except for occasional swaps:
    swap a case with a later one when only that restores lap-count agreement."""
    cases = list(cases)
    for i, race in enumerate(races):
        if cases[i][1] == race.get('laps'):
            continue
        for j in range(i + 1, len(cases)):
            if cases[j][1] == race.get('laps') and cases[i][1] == races[j].get('laps'):
                report.append(f'- {year}: template keys {cases[i][0]} and {cases[j][0]} are out of calendar order; matched by lap count')
                cases[i], cases[j] = cases[j], cases[i]
                break
    return cases


def load_lap_leaders(path: str) -> dict:
    leaders = defaultdict(dict)
    with open(path, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['position'] == '1':
                leaders[int(r['raceId'])][int(r['lap'])] = r['driverId']
    return leaders


def main() -> None:
    raw_dir, root, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    lap_times = sys.argv[4] if len(sys.argv) > 4 else None
    drivers = load_drivers(root)
    lap_leaders = load_lap_leaders(lap_times) if lap_times else {}

    out_rows = []
    report = []
    totals = defaultdict(int)
    agreement = {'laps': 0, 'agree': 0, 'races': 0, 'exact_races': 0, 'diff': []}

    for path in sorted(glob.glob(f'{raw_dir}/*.json')):
        year = int(os.path.basename(path)[:4])
        with open(path, encoding='utf-8') as fh:
            page = json.load(fh)
        cases = parse_template(page['wikitext'])
        races = load_races(root, year)
        if len(cases) != len(races):
            report.append(f'- **{year}**: {len(cases)} template races vs {len(races)} in F1DB — season skipped')
            totals['season_mismatch'] += 1
            continue
        cases = align(cases, races, report, year)
        for (key, period, stints, problems, parse_notes), race in zip(cases, races):
            rows, errors, notes = validate(race, period, stints, drivers)
            errors = problems + errors
            notes = parse_notes + notes
            label = f"{year} R{race['round']} {race['grandPrixId']} ({key})"
            totals['races'] += 1
            if errors:
                totals['failed'] += 1
                report.append(f'- **{label}** — FAILED: ' + '; '.join(errors))
                continue
            totals['passed'] += 1
            for n in dict.fromkeys(notes):
                report.append(f'- {label} — note: {n}')
            if FIRST_OUTPUT_YEAR <= year <= LAST_OUTPUT_YEAR:
                totals['output_races'] += 1
                for did, first, last, name in rows:
                    out_rows.append(
                        {
                            'raceId': race['id'],
                            'year': year,
                            'round': race['round'],
                            'grandPrixId': race['grandPrixId'],
                            'driverId': did,
                            'firstLap': first,
                            'lastLap': last,
                            'laps': last - first + 1,
                            'source': 'wikipedia',
                            'sourcePage': page['title'],
                            'sourceRevision': page['revid'],
                            'sourceKey': key,
                        }
                    )
            elif race['id'] in lap_leaders:
                lead = lap_leaders[race['id']]
                agreement['races'] += 1
                diffs = []
                for did, first, last, _ in rows:
                    for lap in range(first, last + 1):
                        if lap in lead:
                            agreement['laps'] += 1
                            if lead[lap] == did:
                                agreement['agree'] += 1
                            else:
                                diffs.append(lap)
                if not diffs:
                    agreement['exact_races'] += 1
                elif len(agreement['diff']) < 40:
                    agreement['diff'].append(f'{label}: {len(diffs)} laps differ (e.g. lap {diffs[0]})')

    os.makedirs(out_dir, exist_ok=True)
    fields = [
        'raceId', 'year', 'round', 'grandPrixId', 'driverId', 'firstLap', 'lastLap', 'laps',
        'source', 'sourcePage', 'sourceRevision', 'sourceKey',
    ]
    with open(f'{out_dir}/lap-leaders.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(out_rows, key=lambda r: (r['year'], r['round'], r['firstLap'])))

    pct = 100 * agreement['agree'] / agreement['laps'] if agreement['laps'] else 0
    lines = [
        '# Lap leaders — validation report',
        '',
        'Generated by `tools/compile.py`. Every race is checked against F1DB (laps, winner, entrants).',
        '',
        f"- Template races checked: {totals['races']} (passed {totals['passed']}, failed {totals['failed']})",
        f"- Seasons skipped for a race-count mismatch: {totals['season_mismatch']}",
        f"- Races written to `lap-leaders.csv` ({FIRST_OUTPUT_YEAR}–{LAST_OUTPUT_YEAR}): {totals['output_races']}",
        f"- Stints written: {len(out_rows)}",
        '',
        '## Accuracy against F1DB lap times (1982 onward)',
        '',
        f"- Races compared: {agreement['races']}; identical leader on every lap: {agreement['exact_races']}",
        f"- Laps compared: {agreement['laps']}; same leader: {agreement['agree']} ({pct:.2f} %)",
        '',
    ]
    lines += [f'- {d}' for d in agreement['diff']]
    lines += ['', '## Per-race findings', ''] + (report or ['- none'])
    with open(f'{out_dir}/VALIDATION.md', 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:16]))


if __name__ == '__main__':
    main()
