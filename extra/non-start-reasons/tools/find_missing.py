#!/usr/bin/env python3
"""List F1DB race-result rows that are non-starts without a reason.

Usage: python3 -I find_missing.py <f1db-root> > missing.json

Statuses: DNS, DNP, EX, DSQ with an empty `reasonRetired`. DNQ / DNPQ are
left out on purpose: the status itself is the reason.
"""

import glob
import json
import os
import sys

import yaml


def main() -> None:
    root = sys.argv[1]
    rows = []
    for path in sorted(glob.glob(f'{root}/src/data/seasons/*/races/*/race-results.yml')):
        with open(path, encoding='utf-8') as fh:
            results = yaml.safe_load(fh) or []
        with open(os.path.join(os.path.dirname(path), 'race.yml'), encoding='utf-8') as fh:
            race = yaml.safe_load(fh)
        year = int(path.split('/seasons/')[1].split('/')[0])
        for r in results:
            pos = r.get('position')
            if isinstance(pos, str) and pos.upper() in ('DNS', 'DNP', 'EX', 'DSQ') and not (r.get('reasonRetired') or '').strip():
                rows.append(
                    {
                        'raceId': race['id'],
                        'year': year,
                        'round': race['round'],
                        'grandPrixId': race['grandPrixId'],
                        'driverId': r['driverId'],
                        'status': pos.upper(),
                        'driverNumber': r.get('driverNumber'),
                    }
                )
    json.dump(rows, sys.stdout, ensure_ascii=False)


if __name__ == '__main__':
    main()
