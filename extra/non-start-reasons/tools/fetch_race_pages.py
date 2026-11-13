#!/usr/bin/env python3
"""Download the Wikipedia race articles needed for missing non-start reasons.

Usage: python3 -I fetch_race_pages.py <missing.json> <f1db-root> <out-dir>

<missing.json> lists rows ({raceId, year, grandPrixId, ...}) from
find_missing.py. For each race the article "<year> <Grand Prix full name>"
is fetched (redirects followed) as rendered HTML with its revision id.
One request per second with an identifying User-Agent.
"""

import json
import sys
import time
import urllib.parse
import urllib.request

import yaml

API = 'https://en.wikipedia.org/w/api.php'
UA = 'f1db-non-start-reasons-compile/1.0 (TracingInsights; contact@tracinginsights.com)'


def fetch(title: str) -> dict:
    query = urllib.parse.urlencode(
        {
            'action': 'parse',
            'page': title,
            'prop': 'text|revid',
            'redirects': '1',
            'format': 'json',
            'formatversion': '2',
        }
    )
    req = urllib.request.Request(f'{API}?{query}', headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if 'error' in data:
        raise RuntimeError(data['error'].get('info'))
    p = data['parse']
    return {'title': p['title'], 'revid': p['revid'], 'html': p['text']}


def main() -> None:
    missing_path, root, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(missing_path, encoding='utf-8') as fh:
        rows = json.load(fh)
    races = {}
    for r in rows:
        races.setdefault(r['raceId'], r)
    for race_id, r in sorted(races.items()):
        with open(f"{root}/src/data/grands-prix/{r['grandPrixId']}.yml", encoding='utf-8') as fh:
            gp = yaml.safe_load(fh)
        title = f"{r['year']} {gp['fullName']}"
        try:
            page = fetch(title)
        except Exception as exc:
            print(f'{race_id} {title}: FAILED {exc}', file=sys.stderr)
            continue
        with open(f'{out_dir}/{race_id}.json', 'w', encoding='utf-8') as fh:
            json.dump(page, fh, ensure_ascii=False)
        print(f'{race_id} {page["title"]}: rev {page["revid"]}')
        time.sleep(1)


if __name__ == '__main__':
    main()
