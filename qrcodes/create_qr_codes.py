#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Create print-ready QR code signage for Kuckuck Werners Berg.

Per URL this generates two artifacts:
  * An SVG artwork at trim size 120x140mm: the QR code (error correction
    level H with a 3-module quiet zone) fills the top 12x12cm, optionally
    with the color logo embedded in the center. Below sits a 2cm title
    band styled like the website header: #2C3E50 with white "Kuckuck
    Werners Berg" in Roboto Bold, converted to vector outlines.
  * A print-ready CMYK PDF following the print shop's data guidelines:
    3mm bleed (the band runs into the bottom bleed), crop marks,
    Trim-/BleedBox, PDF version 1.4, no embedded ICC profiles, vector
    only. The logo is fully embedded, so both files are single
    self-contained artifacts (the PDF for the print shop, the SVG for
    viewing and further processing).

Example call:
    ./create_qr_codes.py --url "https://wernersberg.de/kwb/1" \
            --logo ../logos/Kombiniert_vector_color.svg --output 1.svg
"""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib

import pikepdf
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

# --- layout constants (mm) ---
TRIM_W, TRIM_H = 120.0, 140.0
BAND_H = 20.0
QR_MARGIN_MODULES = 3
LOGO_RATIO = 0.20
LOGO_BG_PAD = 0.03
TEXT_PADDING = 3.0
BLEED = 3.0
MARK_LEN = 3.0
MARK_MARGIN = BLEED + MARK_LEN
OFFSET = BLEED + MARK_MARGIN
MEDIA_W, MEDIA_H = TRIM_W + 2 * OFFSET, TRIM_H + 2 * OFFSET
MARK_STROKE = 0.15

BAND_COLOR = '#2C3E50'
TEXT_COLOR = '#FFFFFF'
MARK_COLOR = '#000000'
BG_COLOR = '#FFFFFF'
TITLE = 'Kuckuck Werners Berg'

PT_PER_MM = 72.0 / 25.4

SVG_NS = 'http://www.w3.org/2000/svg'

def _q(tag):
    return f'{{{SVG_NS}}}{tag}'

def register_namespaces():
    ET.register_namespace('', SVG_NS)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
    ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')


def run_qrencode(url):
    """Generate the QR code SVG and return (parsed root, viewBox size)."""
    cmd = [
        'qrencode',
        '--level=H',
        f'--margin={QR_MARGIN_MODULES}',
        '--type=SVG',
        '--output=-',
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("Error: 'qrencode' is not installed.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error executing qrencode: {e.stderr}")
    root = ET.fromstring(result.stdout)
    viewbox = root.get('viewBox')
    if not viewbox:
        sys.exit("Error: unexpected qrencode SVG output (no viewBox).")
    size = float(viewbox.split()[2])
    return root, size


def logo_geometry(qr_size, qr_scale):
    """Return x, y, size of the logo centered in the QR area."""
    pattern_mm = (qr_size - 2 * QR_MARGIN_MODULES) * qr_scale
    logo_size = LOGO_RATIO * pattern_mm
    return (TRIM_W - logo_size) / 2.0, (TRIM_W - logo_size) / 2.0, logo_size


def make_logo_element(logo_path, geometry):
    """Build the logo group (white backing + embedded logo).

    The logo content itself is inlined, keeping every generated file
    (artwork SVG and print PDF) self-contained.
    """
    x, y, size = geometry
    pad = size * LOGO_BG_PAD
    group = ET.Element(_q('g'))
    ET.SubElement(group, _q('rect'), {
        'x': f'{x - pad:.4f}',
        'y': f'{y - pad:.4f}',
        'width': f'{size + 2 * pad:.4f}',
        'height': f'{size + 2 * pad:.4f}',
        'fill': BG_COLOR,
    })
    logo_root = ET.parse(logo_path).getroot()
    viewbox = logo_root.get('viewBox')
    if not viewbox:
        sys.exit(f"Error: logo {logo_path} has no viewBox.")
    inner = ET.SubElement(group, _q('svg'), {
        'x': f'{x:.4f}',
        'y': f'{y:.4f}',
        'width': f'{size:.4f}',
        'height': f'{size:.4f}',
        'viewBox': viewbox,
    })
    for child in logo_root:
        inner.append(child)
    return group


def find_roboto_bold():
    """Locate Roboto-Bold.ttf in the usual system font directories."""
    bases = [
        '/usr/share/fonts',
        '/usr/local/share/fonts',
        os.path.expanduser('~/.fonts'),
        os.path.expanduser('~/.local/share/fonts'),
    ]
    for base in bases:
        for dirpath, _, filenames in os.walk(base):
            if 'Roboto-Bold.ttf' in filenames:
                return os.path.join(dirpath, 'Roboto-Bold.ttf')
    sys.exit("Error: Roboto-Bold.ttf not found (sudo apt install fonts-roboto).")


def add_title(elements, band_y):
    """Render the title as vector outlines, fitted into the band."""
    font = TTFont(find_roboto_bold())
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font['hmtx']
    upm = font['head'].unitsPerEm
    cap = font['OS/2'].sCapHeight

    glyphs = []
    pen_x = 0.0
    for ch in TITLE:
        gname = cmap.get(ord(ch))
        if gname is None:
            sys.exit(f"Error: no glyph for {ch!r} in Roboto Bold.")
        pen = SVGPathPen(glyph_set)
        glyph_set[gname].draw(pen)
        commands = pen.getCommands()
        if commands:
            glyphs.append((pen_x, commands))
        pen_x += hmtx[gname][0]

    avail_w = TRIM_W - 2 * TEXT_PADDING
    avail_h = BAND_H - 2 * TEXT_PADDING
    scale = min(avail_w / pen_x, avail_h * upm / cap)
    cap_mm = cap * scale
    baseline = band_y + (BAND_H + cap_mm) / 2.0
    x_start = (TRIM_W - pen_x * scale) / 2.0

    group = ET.Element(_q('g'), {'fill': TEXT_COLOR})
    for pen_x_glyph, commands in glyphs:
        ET.SubElement(group, _q('path'), {
            'd': commands,
            'transform': (
                f'translate({x_start + pen_x_glyph * scale:.4f} '
                f'{baseline:.4f}) scale({scale:.6f} {-scale:.6f})'
            ),
        })
    elements.append(group)


def build_artwork_content(url, logo_path):
    """Build the artwork children plus the logo geometry (logo element is
    inserted by the callers)."""
    qr_root, qr_size = run_qrencode(url)
    qr_scale = TRIM_W / qr_size

    elements = []
    elements.append(ET.Element(_q('rect'), {
        'x': '0', 'y': '0',
        'width': f'{TRIM_W}', 'height': f'{TRIM_H}',
        'fill': BG_COLOR,
    }))

    qr_group = ET.Element(_q('g'), {'transform': f'scale({qr_scale:.6f})'})
    for child in qr_root:
        qr_group.append(child)
    elements.append(qr_group)

    band_y = TRIM_W  # band sits directly below the 12x12cm QR area
    elements.append(ET.Element(_q('rect'), {
        'x': '0', 'y': f'{band_y}',
        'width': f'{TRIM_W}', 'height': f'{BAND_H}',
        'fill': BAND_COLOR,
    }))
    add_title(elements, band_y)

    geometry = logo_geometry(qr_size, qr_scale) if logo_path else None
    return elements, geometry


def write_artwork_svg(path, elements, logo_path, geometry):
    svg = ET.Element(_q('svg'), {
        'width': '12cm', 'height': '14cm',
        'viewBox': f'0 0 {TRIM_W:g} {TRIM_H:g}',
        'version': '1.1',
    })
    for element in elements:
        svg.append(element)
    if geometry:
        svg.insert(2, make_logo_element(logo_path, geometry))
    ET.ElementTree(svg).write(path, encoding='utf-8', xml_declaration=True)


def build_print_svg_bytes(elements, logo_path, geometry):
    """Wrap the artwork at trim offset, extend the band into the bleed,
    and add crop marks. Returns SVG bytes ready for PDF conversion."""
    svg = ET.Element(_q('svg'), {
        'width': f'{MEDIA_W:g}mm', 'height': f'{MEDIA_H:g}mm',
        'viewBox': f'0 0 {MEDIA_W:g} {MEDIA_H:g}',
        'version': '1.1',
    })
    svg.append(ET.Element(_q('rect'), {
        'x': '0', 'y': '0',
        'width': f'{MEDIA_W:g}', 'height': f'{MEDIA_H:g}',
        'fill': BG_COLOR,
    }))
    # Band extended by the bleed on all sides (only visible in the bleed area).
    svg.append(ET.Element(_q('rect'), {
        'x': f'{MARK_MARGIN:g}',
        'y': f'{OFFSET + TRIM_W:g}',
        'width': f'{TRIM_W + 2 * BLEED:g}',
        'height': f'{BAND_H + BLEED:g}',
        'fill': BAND_COLOR,
    }))
    inner = ET.Element(_q('svg'), {
        'x': f'{OFFSET:g}', 'y': f'{OFFSET:g}',
        'width': f'{TRIM_W:g}', 'height': f'{TRIM_H:g}',
        'viewBox': f'0 0 {TRIM_W:g} {TRIM_H:g}',
    })
    for element in elements:
        inner.append(element)
    if geometry:
        inner.insert(2, make_logo_element(logo_path, geometry))
    svg.append(inner)

    # Crop marks: aligned with the trim edges, drawn outside the bleed.
    marks = ET.Element(_q('g'), {
        'stroke': MARK_COLOR,
        'stroke-width': f'{MARK_STROKE:g}',
        'fill': 'none',
    })
    trim_l, trim_r = OFFSET, OFFSET + TRIM_W
    trim_t, trim_b = OFFSET, OFFSET + TRIM_H
    segments = []
    for x in (trim_l, trim_r):
        segments += [
            (x, trim_t - MARK_MARGIN, x, trim_t - BLEED),
            (x, trim_b + BLEED, x, trim_b + MARK_MARGIN),
        ]
    for y in (trim_t, trim_b):
        segments += [
            (trim_l - MARK_MARGIN, y, trim_l - BLEED, y),
            (trim_r + BLEED, y, trim_r + MARK_MARGIN, y),
        ]
    for x1, y1, x2, y2 in segments:
        ET.SubElement(marks, _q('path'), {'d': f'M {x1:g} {y1:g} L {x2:g} {y2:g}'})
    svg.append(marks)
    return ET.tostring(svg, encoding='utf-8')


def svg_to_pdf(print_svg_bytes, tmp_pdf_path):
    """Convert the print SVG to a PDF page at media size."""
    cmd = [
        'rsvg-convert',
        '--format=pdf',
        f'--page-width={MEDIA_W:g}mm',
        f'--page-height={MEDIA_H:g}mm',
        '--keep-aspect-ratio',
        '-o', tmp_pdf_path,
        '-',
    ]
    try:
        subprocess.run(cmd, input=print_svg_bytes, check=True,
                        capture_output=True)
    except FileNotFoundError:
        sys.exit("Error: 'rsvg-convert' is not installed (librsvg2-bin).")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error executing rsvg-convert: {e.stderr.decode()}")


def pdf_to_cmyk(tmp_pdf_path, out_pdf_path):
    """Convert to CMYK (DeviceCMYK, no ICC), PDF 1.4, with Trim/BleedBox."""
    trim_box = [OFFSET, OFFSET, OFFSET + TRIM_W, OFFSET + TRIM_H]
    bleed_box = [MARK_MARGIN, MARK_MARGIN,
                 MARK_MARGIN + TRIM_W + 2 * BLEED,
                 MARK_MARGIN + TRIM_H + 2 * BLEED]
    trim_pts = ' '.join(f'{v * PT_PER_MM:.3f}' for v in trim_box)
    bleed_pts = ' '.join(f'{v * PT_PER_MM:.3f}' for v in bleed_box)
    pdfmark = f'[ /TrimBox [ {trim_pts} ] /BleedBox [ {bleed_pts} ] /PAGES pdfmark'
    cmd = [
        'gs',
        '-dBATCH', '-dNOPAUSE', '-dSAFER',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-sColorConversionStrategy=CMYK',
        '-dProcessColorModel=/DeviceCMYK',
        '-o', out_pdf_path,
        '-c', pdfmark,
        '-f', tmp_pdf_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("Error: 'gs' is not installed (ghostscript).")
    if result.returncode != 0:
        sys.exit(f"Error executing gs: {result.stderr}")
    for line in result.stderr.splitlines():
        if 'Error' in line or 'error' in line:
            print(f"gs: {line}", file=sys.stderr)


CMYK_BLACK_RE = re.compile(rb'([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) (k|K)\b')


def enforce_pure_black(pdf_path):
    """Rewrite rich-black CMYK fills/strokes to pure K.

    Ghostscript's RGB->CMYK conversion maps pure black (#000000) to a
    rich black (~295% total ink). On the QR modules and crop marks that
    risks CMY registration fringes, so those operators are converted to
    0 0 0 1 (K only). Dark values of the embedded artwork are not
    affected since they differ clearly from the converted pure black.
    """
    changed = 0

    def rewrite(match):
        nonlocal changed
        c, m, y, k, op = match.groups()
        if min(float(c), float(m), float(y)) >= 0.6 and float(k) >= 0.8:
            changed += 1
            return b'0 0 0 1 ' + op
        return match.group(0)

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        for obj in pdf.objects:
            if not isinstance(obj, pikepdf.Stream):
                continue
            data = obj.read_bytes()
            patched = CMYK_BLACK_RE.sub(rewrite, data)
            if patched != data:
                obj.write(zlib.compress(patched),
                          filter=pikepdf.Name('/FlateDecode'))
        pdf.save(pdf_path)
    os.chmod(pdf_path, 0o644)

    if changed == 0:
        print('Warning: no rich-black operators found to normalize '
              '(ghostscript behavior changed?)', file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Generate a QR code sign as artwork SVG and print-ready CMYK '
            'PDF (12x14cm with title band).'
        )
    )
    parser.add_argument(
        '-u', '--url', required=True,
        help="The URL to encode (e.g. https://wernersberg.de/kwb/1)",
    )
    parser.add_argument(
        '-l', '--logo', required=False, default=None,
        help="Optional logo SVG embedded in the QR code center "
             "(in both the artwork SVG and the print PDF)",
    )
    parser.add_argument(
        '-o', '--output', required=True,
        help="Path for the artwork SVG (the PDF is written alongside)",
    )
    args = parser.parse_args()

    register_namespaces()
    elements, geometry = build_artwork_content(args.url, args.logo)

    write_artwork_svg(args.output, elements, args.logo, geometry)
    print(f"Success! Artwork SVG saved to '{args.output}'.")

    svg_pdf = os.path.splitext(args.output)[0] + '.pdf'
    tmp_pdf = os.path.splitext(args.output)[0] + '.rgb.pdf'
    svg_to_pdf(build_print_svg_bytes(elements, args.logo, geometry), tmp_pdf)
    pdf_to_cmyk(tmp_pdf, svg_pdf)
    os.remove(tmp_pdf)
    enforce_pure_black(svg_pdf)
    print(f"Success! Print-ready CMYK PDF saved to '{svg_pdf}'.")


if __name__ == '__main__':
    main()
