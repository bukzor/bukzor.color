"""Color encoding registry and auto-parsing."""

import re

from bukzor_color.encodings import base
from bukzor_color.encodings import hex as hex_enc
from bukzor_color.encodings import hsl
from bukzor_color.encodings import hsv
from bukzor_color.encodings import rgb
from bukzor_color.encodings import wcag_hcl

ColorEncoding = base.ColorEncoding
HexEncoding = hex_enc.HexEncoding
HSLEncoding = hsl.HSLEncoding
HSVEncoding = hsv.HSVEncoding
RGBEncoding = rgb.RGBEncoding
WcagHCLEncoding = wcag_hcl.WcagHCLEncoding


def auto_parse(text: str) -> ColorEncoding:
    """Auto-detect and parse any color encoding format."""
    text = text.strip()

    # Try hex format first
    if text.startswith("#") or re.match(r"^[0-9a-fA-F]{3,6}$", text):
        return HexEncoding.parse(text)

    # Try function formats
    if text.startswith("rgb("):
        return RGBEncoding.parse(text)
    if text.startswith("hsl("):
        return HSLEncoding.parse(text)
    if text.startswith("hsv("):
        return HSVEncoding.parse(text)
    if text.startswith("wcag-hcl("):
        return WcagHCLEncoding.parse(text)

    # Try CSS named colors by converting to hex first
    from bukzor_color.parse import CSS_NAMED_COLORS

    if text.lower() in CSS_NAMED_COLORS:
        hex_value = CSS_NAMED_COLORS[text.lower()]
        return HexEncoding.parse(hex_value)

    raise ValueError(f"Cannot auto-detect color format: {text}")
