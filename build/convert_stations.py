#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert station/*.md to station/*.yaml, filling in TODOs."""

import os
import re
import yaml

STATIC_KUCKUCK_INTRO = '"Habt Ihr den Kuckuck Werner schon gehört?" "Nein, ja leider ist er selten geworden, aber suche doch mal …'

def fill_todos(station_id, section, content):
    """Fill in TODO content based on station and section."""
    if station_id == 0 and section == 'fuchs':
        return (
            "Hoch oben am Rothenberg, in einer alten knorrigen Kiefer, wohnt ein ganz besonderer "
            "Kuckuck. Sein Name ist Werner – Kuckuck Werner! Eigentlich ruft Werner jedes Jahr "
            "pünktlich zum Frühling sein fröhliches „Ku-ckuck“ über die Dächer von Wernersberg. "
            "Doch in diesem Jahr ist etwas seltsam: Werner ist verschwunden! Niemand hat ihn "
            "gehört, niemand hat ihn gesehen.\n\n"
            "Die Tiere des Waldes sind in großer Sorge: Wo steckt nur Kuckuck Werner? Hat er sich "
            "versteckt? Braucht er Hilfe? Deshalb haben sich seine tierischen Freunde – der schlaue "
            "Fuchs, das flinke Eichhörnchen und viele Vögel – zusammengetan und einen Suchtrupp "
            "gebildet. Sie brauchen dringend deine Unterstützung!\n\n"
            "Begib dich auf die Spur von Kuckuck Werner rund um den Rothenberg und hilf mit, ihn "
            "zu finden. Auf deinem Weg erwarten dich spannende Rätsel, lustige Bewegungsspiele und "
            "viele interessante Geschichten über den Wald und seine Bewohner.\n\n"
            "Bist du bereit? Dann nichts wie los – Kuckuck Werner wartet auf dich!"
        )
    if station_id == 0 and section == 'eichhoernchen':
        return (
            "**So funktioniert der Erlebnisweg:**\n\n"
            "Im Wald findest du an verschiedenen Stellen kleine Schilder mit QR-Codes. "
            "Scanne den QR-Code einfach mit deinem Smartphone – schon öffnet sich die passende "
            "Stationsseite mit spannenden Infos, lustigen Spielen und dem Vogel-Suchspiel.\n\n"
            "Auf jeder Seite findest du drei Abschnitte:\n"
            "- **Fuchs: „Schon gewusst?\"** – Spannendes Wissen über den Wald\n"
            "- **Eichhörnchen: „Schon bewegt?\"** – Lustige Bewegungsspiele\n"
            "- **Kuckuck: „Schon gehört oder gar gefunden?\"** – Finde den versteckten Vogel\n\n"
            "Am Ende des Weges wartet eine große Überraschung auf dich. "
            "Viel Spaß auf deiner Entdeckungstour!"
        )
    if station_id == 5 and section == 'eichhoernchen':
        return (
            "Der Pfad ist hier recht schmal, also machen wir eine Übung auf der Stelle! "
            "Stell dich auf ein Bein und versuche, das Gleichgewicht zu halten. Zähle bis 20. "
            "Schaffst du es, ohne den Boden mit dem anderen Fuß zu berühren? Wenn das zu einfach "
            "ist, schließe die Augen dabei! Das trainiert deinen Gleichgewichtssinn und macht "
            "auch noch Spaß. Wechsle danach das Bein und probiere es noch einmal!"
        )
    if station_id == 9 and section == 'fuchs':
        return (
            "Von diesem Aussichtspunkt aus blickst du auf eine der burgenreichsten Regionen "
            "Deutschlands. Im Mittelalter, zur Zeit der Stauferkaiser im 12. und 13. Jahrhundert, "
            "erlebten die Burgen hier ihre Blütezeit. Der berühmteste unter den Staufern, Kaiser "
            "Friedrich Barbarossa, ließ die Reichsburg Trifels zur Reichsfeste ausbauen. Hier "
            "wurden sogar die Reichskleinodien – Krone, Zepter und Reichsapfel – aufbewahrt!\n\n"
            "Die Staufer kontrollierten von diesen Höhenburgen aus die wichtigen Handelswege durch "
            "das Trifelsland. Neben dem Trifels entstanden in Sichtweite die Burgen Anebos und "
            "Scharfenberg, die zusammen eine beeindruckende Burgenlandschaft bilden. Richard "
            "Löwenherz, der englische König, war übrigens von 1193 bis 1194 Gefangener auf dem "
            "Trifels – eine der bekanntesten Geschichten der Region!\n\n"
            "Die Stauferzeit endete im 13. Jahrhundert, doch die Burgen prägen bis heute das "
            "Landschaftsbild und sind beliebte Ausflugsziele."
        )
    if station_id == 13 and section == 'fuchs':
        return (
            "Im Pfälzer Wald gibt es ein dichtes Netz an Rastmöglichkeiten für Wanderer. "
            "Allein der Pfälzerwald-Verein unterhält über 100 Schutzhütten, die meisten davon "
            "frei zugänglich und mit Sitzgelegenheiten und oft auch einer Feuerstelle ausgestattet.\n\n"
            "Daneben gibt es bewirtschaftete Hütten, die an Wochenenden und Feiertagen geöffnet "
            "sind und regionale Spezialitäten wie Saumagen, Bratwurst oder Pfälzer Weine anbieten. "
            "Besonders beliebt sind die Hütten des Pfälzerwald-Vereins wie die Landauer Hütte oder "
            "die Trifels-Hütte.\n\n"
            "Einfache Bänke entlang der Wege laden immer wieder zum kurzen Verweilen ein und "
            "wurden oft von ortsansässigen Vereinen oder Privatpersonen gestiftet. Schau dich "
            "mal um, ob du auf den Bänken Widmungen oder kleine Tafeln entdecken kannst!"
        )
    if station_id == 15 and section == 'fuchs':
        return (
            "Das Wernersberger Wappen zeigt einen goldenen Kuckuck auf grünem Dreiberg, dahinter "
            "eine rote Burg mit zwei Zinnentürmen. Die Burg im Wappen erinnert an die einstige "
            "Burg der Herren von Wernhersberc, die dem Ort seinen Namen gab. Erstmals urkundlich "
            "erwähnt wurde Wernersberg im Jahr 1276.\n\n"
            "Der Kuckuck im Wappen verweist auf den „Uznamen\" der Wernersberger Bürger: "
            "Die Einwohner werden traditionell „Kuckucke\" genannt, was sich vermutlich von der "
            "Kirchweih ableitet, die am zweiten Maisonntag – wenn der Kuckuck ruft – gefeiert "
            "wird.\n\n"
            "Der grüne Dreiberg symbolisiert die Lage des Ortes am Rothenberg im Pfälzer Wald. "
            "Die Farben Rot und Gold sind die traditionellen Farben der Pfalz und unterstreichen "
            "die regionale Verbundenheit."
        )
    if station_id == 16 and section == 'kuckuck':
        # For kuckuck section, we need hint and placement
        return ('"…dort wo das Licht durch die Blätter fällt"', "An einem sonnenbeschienenen Baum")
    if station_id == 17 and section == 'kuckuck':
        return ('"…dort wo der Boden aufgewühlt ist"', "An einer Wildschwein-Suhle nahe des Weges")
    return content


def parse_markdown(filepath):
    """Parse a station markdown file into structured data."""
    with open(filepath) as f:
        text = f.read()

    lines = text.strip().split('\n')

    # Extract title from first heading
    title_match = re.match(r'^#+\s*(.+)', lines[0])
    title = title_match.group(1).strip() if title_match else "Unbekannte Station"

    sections = {'fuchs': '', 'eichhoernchen': '', 'kuckuck': '', 'placement': '', 'vogel': ''}
    current_section = None
    section_patterns = {
        'fuchs': re.compile(r'##\s+Fuchs:?\s*.*', re.IGNORECASE),
        'eichhoernchen': re.compile(r'##\s+Eichh[öo]rnchen:?\s*.*', re.IGNORECASE),
        'kuckuck': re.compile(r'##\s+Kuckuck:?\s*.*', re.IGNORECASE),
        'placement': re.compile(r'##\s+Platzierung:?\s*.*', re.IGNORECASE),
        'vogel': re.compile(r'##\s+Vogel:?\s*.*', re.IGNORECASE),
    }

    for line in lines[1:]:
        matched = False
        for key, pattern in section_patterns.items():
            if pattern.match(line):
                current_section = key
                matched = True
                break
        if matched:
            continue
        if current_section:
            sections[current_section] += line + '\n'

    return {
        'title': title,
        'fuchs': sections['fuchs'].strip(),
        'eichhoernchen': sections['eichhoernchen'].strip(),
        'kuckuck_hint': sections['kuckuck'].strip(),
        'placement': sections['placement'].strip(),
    }


def convert_all():
    """Convert all station markdown files to YAML."""
    os.makedirs('station', exist_ok=True)
    yaml_files = []

    for num in range(0, 19):
        md_path = f'station/station{num:02}.md'
        if not os.path.exists(md_path):
            continue

        data = parse_markdown(md_path)

        # Fill TODOs and placeholder topics
        for section in ['fuchs', 'eichhoernchen']:
            needs_fill = 'TODO' in data[section] or data[section].startswith('Thema:')
            if needs_fill:
                data[section] = fill_todos(num, section, data[section])

        has_hint_todo = 'TODO' in data['kuckuck_hint'] or data['kuckuck_hint'] == ''
        if has_hint_todo:
            result = fill_todos(num, 'kuckuck', data['kuckuck_hint'])
            if result and isinstance(result, tuple):
                data['kuckuck_hint'] = result[0]
                data['placement'] = result[1]

        # Clean up hint text: strip "Hinweis:" prefix, split off "Platzierung:" if present
        hint_text = data['kuckuck_hint']
        if 'Hinweis:' in hint_text:
            hint_text = hint_text.replace('Hinweis:', '').strip()
        # If Platzierung is embedded in hint text, extract it
        if '\nPlatzierung:' in hint_text or hint_text.startswith('Platzierung:'):
            parts = hint_text.split('Platzierung:', 1)
            hint_text = parts[0].strip()
            embedded_placement = parts[1].strip() if len(parts) > 1 else ''
            if embedded_placement and not data['placement']:
                data['placement'] = embedded_placement
        data['kuckuck_hint'] = hint_text

        # Clean up placement text: strip "Platzierung:" prefix
        placement_text = data['placement']
        if placement_text.startswith('Platzierung:'):
            placement_text = placement_text.replace('Platzierung:', '').strip()
        data['placement'] = placement_text

        # Build kuckuck dict
        kuckuck = {'hint': data['kuckuck_hint']}
        if data['placement']:
            kuckuck['placement'] = data['placement']

        # For station 00 (intro), the kuckuck section is different - it's the intro text
        # Actually looking at station00.md, it has no sections, it's all intro text
        # Let me handle it specially
        if num == 0:
            yaml_data = {
                'title': 'Willkommen',
                'fuchs': fill_todos(0, 'fuchs', ''),
                'eichhoernchen': fill_todos(0, 'eichhoernchen', ''),
            }
        else:
            yaml_data = {
                'title': data['title'],
                'fuchs': data['fuchs'],
                'eichhoernchen': data['eichhoernchen'],
                'kuckuck': kuckuck,
            }

        yaml_path = f'station/{num:02}.yaml'
        with open(yaml_path, 'w') as f:
            f.write('# SPDX-License-Identifier: CC-BY-SA-4.0\n')
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=100)

        yaml_files.append(yaml_path)
        print(f'Converted: {md_path} -> {yaml_path}')

    return yaml_files


if __name__ == '__main__':
    convert_all()