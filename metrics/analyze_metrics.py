#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later
"""Summarize the anonymous QR redirect metrics as terminal histograms."""

import re
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

LOG = Path('metrics/.ht-qr-redirect-metrics.log')
LINE_RE = re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\t(\d{1,2})$')
WEEKDAY_NAMES = ('Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So')
BAR_WIDTH = 30


def station_title(sid):
    try:
        with open(f'station/{sid:02}.yaml') as f:
            return yaml.safe_load(f)['title']
    except (OSError, KeyError, yaml.YAMLError):
        return f'Station {sid:02}'


def bar(count, max_count):
    return '#' * round(BAR_WIDTH * count / max_count) if max_count else ''


def print_buckets(title, counts):
    max_count = max(counts.values(), default=0)
    print(f'\n{title}')
    for key in sorted(counts):
        c = counts[key]
        print(f'  {key:<12} {c:>6}  {bar(c, max_count)}')


def main():
    try:
        lines = LOG.read_text().splitlines()
    except FileNotFoundError:
        print(f'No metrics data at {LOG} — run "make sync" first.')
        return

    days, weeks, months, weekdays, stations = Counter(), Counter(), Counter(), Counter(), Counter()
    total = skipped = 0
    for line in lines:
        m = LINE_RE.match(line)
        if not m:
            skipped += 1
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            skipped += 1
            continue
        days[m.group(1)] += 1
        iso = d.isocalendar()
        weeks[f'{iso.year}-W{iso.week:02d}'] += 1
        months[m.group(1)[:7]] += 1
        weekdays[d.weekday()] += 1
        stations[int(m.group(3))] += 1
        total += 1

    if not total:
        print('No scans recorded yet.')
        if skipped:
            print(f'({skipped} unparseable lines skipped)')
        return

    first, last = date.fromisoformat(min(days)), date.fromisoformat(max(days))
    print(f'QR redirects total: {total}')
    print(f'Period: {first} to {last}')
    if skipped:
        print(f'({skipped} unparseable lines skipped)')

    print('\nStations')
    max_station = max(stations.values())
    for sid in sorted(stations):
        c = stations[sid]
        print(f'  {sid:>2}  {station_title(sid):<34} {c:>6}  {bar(c, max_station)}')

    print_buckets('Days', days)
    empty = (last - first).days + 1 - len(days)
    if empty:
        print(f'  ({empty} days without scans omitted)')

    print_buckets('Weeks', weeks)
    print_buckets('Months', months)

    print('\nWeekdays')
    max_weekday = max(weekdays.values(), default=0)
    for wd in range(7):
        c = weekdays.get(wd, 0)
        print(f'  {WEEKDAY_NAMES[wd]:<12} {c:>6}  {bar(c, max_weekday)}')


if __name__ == '__main__':
    main()