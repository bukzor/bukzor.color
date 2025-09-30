"""Color formatting to various string representations."""

from decimal import Decimal

from bukzor_color.core import Color


def to_hex(color: Color) -> str:
    """Format color as hex string like '#ff0000'."""
    return color.to_hex()


def to_rgb_string(color: Color) -> str:
    """Format color as RGB string like 'rgb(255, 0, 0)'."""
    r, g, b = color.to_srgb()
    return f"rgb({r}, {g}, {b})"


def to_hsl_string(color: Color) -> str:
    """Format color as HSL string like 'hsl(240, 100%, 50%)'."""
    h, s, l = color.to_hsl()
    return f"hsl({h:.0f}, {s:.0f}%, {l:.0f}%)"


def to_hsv_string(color: Color) -> str:
    """Format color as HSV string like 'hsv(240, 100%, 50%)'."""
    h, s, v = _color_to_hsv(color)
    return f"hsv({h:.0f}, {s:.0f}%, {v:.0f}%)"


def _color_to_hsv(color: Color) -> tuple[Decimal, Decimal, Decimal]:
    """Convert Color to HSV values (h: 0-360, s,v: 0-100)."""
    # Convert to sRGB first for HSV calculation
    def linear_to_srgb_norm(component: Decimal) -> Decimal:
        if component <= Decimal('0.0031308'):
            return component * Decimal('12.92')
        else:
            return Decimal('1.055') * (component ** (Decimal('1') / Decimal('2.4'))) - Decimal('0.055')

    r_norm = linear_to_srgb_norm(color.red)
    g_norm = linear_to_srgb_norm(color.green)
    b_norm = linear_to_srgb_norm(color.blue)

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val

    # Value
    value = max_val

    # Saturation
    if max_val == 0:
        saturation = Decimal('0')
    else:
        saturation = diff / max_val

    # Hue
    if diff == 0:
        hue = Decimal('0')
    else:
        if max_val == r_norm:
            hue = (g_norm - b_norm) / diff
            if g_norm < b_norm:
                hue += 6
        elif max_val == g_norm:
            hue = (b_norm - r_norm) / diff + 2
        else:  # max_val == b_norm
            hue = (r_norm - g_norm) / diff + 4

        hue *= 60  # Convert to degrees

    return (hue, saturation * 100, value * 100)