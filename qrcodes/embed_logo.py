#!/usr/bin/env python3
"""
Helper around qrencode to embed an SVG logo onto a generated SVG qr code.

Example call:
    ./embed_logo.py --url "https://wernersberg.de/kwb/1" \
            --logo ../logos/Kombiniert_vector_color.svg --output 1-color.svg
"""

import sys
import argparse
import subprocess
import xml.etree.ElementTree as ET


def embed_logo(qr_root: ET.Element, logo_path: str) -> None:
    """Calculates center and add background+logo into the SVG tree root."""
    # Extract internal grid size using viewBox
    viewbox = qr_root.get("viewBox")
    if viewbox:
        _, _, qr_w, qr_h = map(float, viewbox.split())
    else:
        clean_w = qr_root.get("width", "100").rstrip("pxcmminpt")
        clean_h = qr_root.get("height", "100").rstrip("pxcmminpt")
        qr_w, qr_h = float(clean_w), float(clean_h)

    # Calculate target size for the logo (~20% of internal width)
    logo_target_size = qr_w * 0.20

    # Calculate exact center positioning relative to the internal canvas
    x_pos = (qr_w - logo_target_size) / 2
    y_pos = (qr_h - logo_target_size) / 2

    # Group container for positioning
    group = ET.Element("g", {"transform": f"translate({x_pos}, {y_pos})"})

    # White background rectangle with 3% padding to prevent bleed-through
    bg_padding = logo_target_size * 0.03
    white_bg = ET.Element(
        "rect",
        {
            "x": f"{-bg_padding}",
            "y": f"{-bg_padding}",
            "width": f"{logo_target_size + (bg_padding * 2)}",
            "height": f"{logo_target_size + (bg_padding * 2)}",
            "fill": "white",
        },
    )
    group.append(white_bg)

    # Embedded logo element
    logo_element = ET.Element(
        "image",
        {
            "href": logo_path,
            "width": f"{logo_target_size}",
            "height": f"{logo_target_size}",
        },
    )
    group.append(logo_element)

    # Append group to the main SVG tree
    qr_root.append(group)


def main():
    """Parse args and create the base qrcode."""
    parser = argparse.ArgumentParser(
        description="Generates a QR and optionally embeds a logo (SVG) in the center."
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="The URL to encode in the QR code (e.g., https://example.com)",
    )
    parser.add_argument(
        "-l",
        "--logo",
        required=False,
        default=None,
        help="Optional path to the logo SVG to be embedded (e.g., logo.svg)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path for the final output SVG (e.g., final_qr.svg)",
    )

    args = parser.parse_args()

    # Correct namespace for SVG elements
    ET.register_namespace('', "http://www.w3.org/2000/svg")

    try:
        # 1. Call qrencode internally and capture the SVG data
        # --level=H  for high error recovery to be able to recover up to 30%
        #            to allow grabing some of that space while still working
        # --margin=0 ensure 100 of the image width/height is the QR code itself
        cmd = [
            "qrencode",
            "--level=H",
            "--margin=0",
            "--type=SVG",
            "--output=-",
            args.url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 2. Parse the generated SVG string into the XML tree
        qr_root = ET.fromstring(result.stdout)

        # 3. Embed logo if specified
        if args.logo:
            embed_logo(qr_root, args.logo)

        # 4. Save the final vector file
        tree = ET.ElementTree(qr_root)
        tree.write(args.output, encoding="utf-8", xml_declaration=True)
        print(
            f"Success! The final QR code has been saved to '{args.output}'."
        )

    except subprocess.CalledProcessError as e:
        print(f"Error executing qrencode: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'qrencode' is not installed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
