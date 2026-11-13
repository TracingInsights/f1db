#!/usr/bin/env python3
"""Download the Wikipedia lap-leader templates (Template:F1Laps<year>).

Usage: python3 -I fetch_templates.py <out-dir> [first-year] [last-year]

Writes one JSON file per season ({title, revid, wikitext}) into <out-dir>.
One request per second with an identifying User-Agent, per the Wikimedia
API etiquette. The downloaded wikitext is CC BY-SA 4.0 content: it is kept
outside the repository and only the extracted facts (with revision ids)
are committed.
"""

import json
import sys
import time
import urllib.parse
import urllib.request

API = 'https://en.wikipedia.org/w/api.php'
UA = 'f1db-lap-leaders-compile/1.0 (TracingInsights; contact@tracinginsights.com)'


def fetch(title: str) -> dict:
    query = urllib.parse.urlencode(
        {
            'action': 'parse',
            'page': title,
            'prop': 'wikitext|revid',
            'format': 'json',
            'formatversion': '2',
        }
    )
    req = urllib.request.Request(f'{API}?{query}', headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if 'error' in data:
        raise RuntimeError(f"{title}: {data['error'].get('info')}")
    parse = data['parse']
    return {'title': parse['title'], 'revid': parse['revid'], 'wikitext': parse['wikitext']}


def main() -> None:
    out_dir = sys.argv[1]
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1950
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    for year in range(first, last + 1):
        title = f'Template:F1Laps{year}'
        try:
            page = fetch(title)
        except Exception as exc:  # keep going; the compile step reports gaps
            print(f'{year}: FAILED {exc}', file=sys.stderr)
            continue
        with open(f'{out_dir}/{year}.json', 'w', encoding='utf-8') as fh:
            json.dump(page, fh, ensure_ascii=False)
        print(f'{year}: rev {page["revid"]}, {len(page["wikitext"])} chars')
        time.sleep(1)


if __name__ == '__main__':
    main()
