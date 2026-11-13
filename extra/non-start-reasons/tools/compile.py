#!/usr/bin/env python3
"""Compile non-start reasons from Wikipedia race classification tables.

Usage: python3 -I compile.py <missing.json> <raw-dir> <f1db-root> <out-dir>

For every F1DB race-result row with status DNS / DNP / EX / DSQ and no
`reasonRetired`, find the driver's row in the article's classification
tables, require that row to carry a non-start status, and take the
"Time/Retired" (or equivalent) cell as the reason. Rows that cannot be
matched unambiguously are reported, never guessed.
"""

import csv
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser

import yaml

STATUS_TOKENS = {'DNS', 'DNP', 'EX', 'DSQ', 'DQ', 'NC', 'DNQ', 'DNPQ', 'WD', 'RET'}
GENERIC = {'nonstarter', 'didnotstart', 'dns', 'dnp', 'disqualified', 'excluded', 'dsq', 'ex', ''}
REASON_HEADERS = ('time/retired', 'time / retired', 'retired', 'reason', 'notes', 'time')


def norm(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z]', '', text.lower())


class Tables(HTMLParser):
    """Collect every <table> as a list of rows of cell texts."""

    def __init__(self):
        super().__init__()
        self.tables, self.stack = [], []
        self.row = None
        self.cell = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.stack.append([])
        elif tag == 'tr' and self.stack:
            self.row = []
        elif tag in ('td', 'th') and self.row is not None:
            self.cell = []
        elif tag in ('sup', 'style') :
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('sup', 'style') and self.skip:
            self.skip -= 1
        elif tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r'\s+', ' ', ''.join(self.cell)).strip())
            self.cell = None
        elif tag == 'tr' and self.row is not None and self.stack:
            if self.row:
                self.stack[-1].append(self.row)
            self.row = None
        elif tag == 'table' and self.stack:
            self.tables.append(self.stack.pop())

    def handle_data(self, data):
        if self.cell is not None and not self.skip:
            self.cell.append(data)


def driver_names(d: dict) -> set:
    names = {norm(d.get('name') or ''), norm(d.get('fullName') or '')}
    names.add(norm(f"{d.get('firstName') or ''}{d.get('lastName') or ''}"))
    return {n for n in names if n}


def main() -> None:
    missing_path, raw_dir, root, out_dir = sys.argv[1:5]
    with open(missing_path, encoding='utf-8') as fh:
        missing = json.load(fh)
    out, report = [], []
    for m in missing:
        label = f"{m['year']} R{m['round']} {m['grandPrixId']} {m['driverId']} ({m['status']})"
        try:
            with open(f"{raw_dir}/{m['raceId']}.json", encoding='utf-8') as fh:
                page = json.load(fh)
        except FileNotFoundError:
            report.append(f'- **{label}** — no article downloaded')
            continue
        with open(f"{root}/src/data/drivers/{m['driverId']}.yml", encoding='utf-8') as fh:
            drv = yaml.safe_load(fh)
        names, surname = driver_names(drv), norm(drv.get('lastName') or '')
        parser = Tables()
        parser.feed(page['html'])
        hits = []
        for table in parser.tables:
            header = next((r for r in table if any(h.lower() in REASON_HEADERS for h in r)), None)
            if not header:
                continue
            lower = [h.lower() for h in header]
            reason_idx = next((lower.index(h) for h in REASON_HEADERS if h in lower), None)
            for row in table:
                if row is header or len(row) < len(header) - 1:
                    continue
                cells = [norm(c) for c in row]
                by_name = any(c in names for c in cells)
                by_surname = not by_name and any(c.endswith(surname) and len(surname) > 3 for c in cells)
                if not (by_name or by_surname):
                    continue
                status = next((c for c in row if c.upper().strip('.') in STATUS_TOKENS), None)
                if not status:
                    continue  # the driver's normal result row, not the non-start entry
                # Column offset: rows can omit the leading position cell.
                off = len(header) - len(row)
                idx = reason_idx - off if reason_idx is not None else None
                reason = row[idx] if idx is not None and 0 <= idx < len(row) else ''
                if reason and reason.upper().strip('.') not in STATUS_TOKENS and not re.fullmatch(r'[\d:.+ ]+', reason):
                    hits.append((reason, status, 'name' if by_name else 'surname'))
        # Prefer rows whose status matches F1DB (a driver can appear twice,
        # e.g. a retirement in one car and a disqualification in another).
        same = [h for h in hits if h[1].upper().replace('DQ', 'DSQ').replace('DSSQ', 'DSQ') == m['status']]
        if same:
            hits = same
        specific = [h for h in hits if norm(h[0]) not in GENERIC]
        if hits and not specific:
            report.append(f'- {label} — Wikipedia gives no reason, only "{hits[0][0]}"')
            continue
        hits = specific
        unique = list(dict.fromkeys(h[0] for h in hits))
        if len(unique) == 1:
            reason, status, how = hits[0]
            out.append(
                {
                    'raceId': m['raceId'], 'year': m['year'], 'round': m['round'],
                    'grandPrixId': m['grandPrixId'], 'driverId': m['driverId'],
                    'status': m['status'], 'reason': reason, 'wikipediaStatus': status.upper(),
                    'source': 'wikipedia', 'sourcePage': page['title'], 'sourceRevision': page['revid'],
                }
            )
            if how != 'name':
                report.append(f'- {label} — matched by surname: "{reason}"')
            if status.upper() != m['status']:
                report.append(f'- {label} — Wikipedia status {status.upper()} differs from F1DB {m["status"]}: "{reason}"')
        elif not unique:
            report.append(f'- **{label}** — no non-start row with a reason found in "{page["title"]}"')
        else:
            report.append(f'- **{label}** — conflicting reasons {unique} in "{page["title"]}"')

    fields = ['raceId', 'year', 'round', 'grandPrixId', 'driverId', 'status', 'reason',
              'wikipediaStatus', 'source', 'sourcePage', 'sourceRevision']
    with open(f'{out_dir}/non-start-reasons.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    lines = [
        '# Non-start reasons — validation report', '',
        f'- F1DB rows without a reason (DNS / DNP / EX / DSQ): {len(missing)}',
        f'- Specific reasons found: {len(out)}',
        f'- No specific reason in Wikipedia, not found, or ambiguous: {len(missing) - len(out)} (listed below)',
        '- Rows marked "differs" have a Wikipedia status that disagrees with F1DB and need a human check before use.', '',
        '## Findings', '',
    ] + (report or ['- none'])
    with open(f'{out_dir}/VALIDATION.md', 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:6]))


if __name__ == '__main__':
    main()
