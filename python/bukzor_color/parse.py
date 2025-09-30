"""Color parsing from various string formats."""

import re
from decimal import Decimal

from bukzor_color.core import Color


def parse_color(color_string: str) -> Color:
    """Parse any supported color format into a Color."""
    color_string = color_string.strip()

    # Try hex format first
    if _is_hex_color(color_string):
        return Color.from_hex(color_string)

    # Try rgb() format
    if color_string.startswith("rgb("):
        return _parse_rgb_string(color_string)

    # Try hsl() format
    if color_string.startswith("hsl("):
        return _parse_hsl_string(color_string)

    # Try hsv() format
    if color_string.startswith("hsv("):
        return _parse_hsv_string(color_string)

    # Try CSS named colors
    if color_string.lower() in CSS_NAMED_COLORS:
        hex_value = CSS_NAMED_COLORS[color_string.lower()]
        return Color.from_hex(hex_value)

    raise ValueError(f"Unrecognized color format: {color_string}")


def _is_hex_color(color_string: str) -> bool:
    """Check if string is a valid hex color."""
    hex_clean = color_string.lstrip("#")
    return bool(re.match(r"^[0-9a-fA-F]{6}$", hex_clean))


def _parse_rgb_string(rgb_string: str) -> Color:
    """Parse RGB string like 'rgb(255, 0, 0)'."""
    match = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", rgb_string)
    if not match:
        raise ValueError(f"Invalid RGB format: {rgb_string}")

    r, g, b = map(int, match.groups())
    return Color.from_srgb(r, g, b)


def _parse_hsl_string(hsl_string: str) -> Color:
    """Parse HSL string like 'hsl(240, 100%, 50%)'."""
    match = re.match(
        r"hsl\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*\)",
        hsl_string,
    )
    if not match:
        raise ValueError(f"Invalid HSL format: {hsl_string}")

    h, s, l = map(Decimal, match.groups())
    return Color.from_hsl(h, s, l)


def _parse_hsv_string(hsv_string: str) -> Color:
    """Parse HSV string like 'hsv(240, 100%, 50%)'."""
    match = re.match(
        r"hsv\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*\)",
        hsv_string,
    )
    if not match:
        raise ValueError(f"Invalid HSV format: {hsv_string}")

    h, s, v = map(Decimal, match.groups())
    return _hsv_to_color(h, s, v)


def _hsv_to_color(h: Decimal, s: Decimal, v: Decimal) -> Color:
    """Convert HSV to Color via sRGB."""
    h_norm = h / Decimal('360')
    s_norm = s / Decimal('100')
    v_norm = v / Decimal('100')

    if s_norm == 0:
        # Achromatic
        gray_val = int(v_norm * 255)
        return Color.from_srgb(gray_val, gray_val, gray_val)

    h_sector = h_norm * 6
    i = int(h_sector)
    f = h_sector - i

    p = v_norm * (1 - s_norm)
    q = v_norm * (1 - s_norm * f)
    t = v_norm * (1 - s_norm * (1 - f))

    if i == 0:
        r, g, b = v_norm, t, p
    elif i == 1:
        r, g, b = q, v_norm, p
    elif i == 2:
        r, g, b = p, v_norm, t
    elif i == 3:
        r, g, b = p, q, v_norm
    elif i == 4:
        r, g, b = t, p, v_norm
    else:  # i == 5
        r, g, b = v_norm, p, q

    return Color.from_srgb(
        int(r * 255),
        int(g * 255),
        int(b * 255)
    )


# CSS Named Colors (subset for common colors)
CSS_NAMED_COLORS = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "silver": "#c0c0c0",
    "gray": "#808080",
    "maroon": "#800000",
    "olive": "#808000",
    "lime": "#00ff00",
    "aqua": "#00ffff",
    "teal": "#008080",
    "navy": "#000080",
    "fuchsia": "#ff00ff",
    "purple": "#800080",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "brown": "#a52a2a",
    "gold": "#ffd700",
    "indigo": "#4b0082",
    "violet": "#ee82ee",
    "crimson": "#dc143c",
    "khaki": "#f0e68c",
    "salmon": "#fa8072",
    "coral": "#ff7f50",
    "turquoise": "#40e0d0",
    "plum": "#dda0dd",
    "tan": "#d2b48c",
}