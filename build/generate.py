#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate static HTML pages for Kuckuck Werners Berg."""

import os
import yaml
import markdown
import subprocess
import glob as globmod
from jinja2 import Environment, FileSystemLoader

VOGEL_DIR = 'vogel'
STATIC_KUCKUCK_INTRO = (
    '"Habt Ihr den Kuckuck Werner schon gehört?" "Nein, ja leider ist er selten '
    'geworden, aber suche doch mal …'
)

def load_station(station_id):
    """Load station YAML and return rendered content."""
    path = f'station/{station_id:02}.yaml'
    with open(path) as f:
        data = yaml.safe_load(f)
    return data

def vogel_files_map():
    """Build a dict mapping bird number (1-18) to filename."""
    m = {}
    for f in sorted(globmod.glob(f'{VOGEL_DIR}/*.png')):
        bn = os.path.basename(f)
        num = int(bn.split('_')[0])
        name = bn.split('_')[1].replace('.png', '')
        m[num] = {'file': bn, 'name': name}
    return m

def get_bird_options(station_id, vmap):
    """Return 3 birds: correct + 2 fixed-offset distractors."""
    offsets = [0, 6, 12]
    birds = []
    correct_prefix = None
    for off in offsets:
        bnum = ((station_id - 1 + off) % 18) + 1
        info = vmap[bnum]
        birds.append(info)
        if off == 0:
            correct_prefix = f'{bnum:02}_'
    return birds, correct_prefix

def render_station(station_id, data, env, vmap, git_sha):
    """Render a single station page."""
    fuchs_html = markdown.markdown(data['fuchs'])
    eich_html = markdown.markdown(data['eichhoernchen'])

    has_kuckuck = 'kuckuck' in data
    if has_kuckuck:
        hint_raw = data['kuckuck']['hint']
        hint_full = f'{STATIC_KUCKUCK_INTRO} {hint_raw}'
        kuckuck_hint_html = markdown.markdown(hint_full)
        birds, correct_prefix = get_bird_options(station_id, vmap)
    else:
        kuckuck_hint_html = None
        birds = None
        correct_prefix = None

    template = env.get_template('station.html.j2')
    html = template.render(
        title=data['title'],
        station_id=station_id,
        fuchs_content=fuchs_html,
        eichhoernchen_content=eich_html,
        kuckuck_hint=kuckuck_hint_html,
        birds=birds,
        correct_prefix=correct_prefix,
        git_sha=git_sha,
        base_path='../',
    )
    os.makedirs('html/station', exist_ok=True)
    out_path = f'html/station/{station_id:02}.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'  Generated: {out_path}')

def render_index(env, git_sha):
    """Render the intro/welcome page."""
    data = load_station(0)
    template = env.get_template('index.html.j2')
    html = template.render(
        title=data['title'],
        story_html=markdown.markdown(data['story']),
        howto_html=markdown.markdown(data['howto']),
        outro=data['outro'],
        git_sha=git_sha,
        base_path='',
    )
    with open('html/index.html', 'w') as f:
        f.write(html)
    print(f'  Generated: html/index.html')

    stationen_html = env.get_template('stationen.html.j2').render(title="Alle Stationen", git_sha=git_sha, base_path='')
    with open('html/stationen.html', 'w') as f:
        f.write(stationen_html)
    print(f'  Generated: html/stationen.html')

def get_git_sha():
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return 'unknown'

def main():
    env = Environment(loader=FileSystemLoader('build/templates'))
    git_sha = get_git_sha()
    vmap = vogel_files_map()

    os.makedirs('html/station', exist_ok=True)

    print('Generating pages…')
    render_index(env, git_sha)

    for sid in range(1, 19):
        try:
            data = load_station(sid)
            render_station(sid, data, env, vmap, git_sha)
        except FileNotFoundError:
            print(f'  Skipping Station {sid:02} (no data file)')

    print('Done.')

if __name__ == '__main__':
    main()