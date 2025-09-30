"""
bukzor.color - Strongly-typed color manipulation library

This library models color as an abstract concept separate from its various
encodings (similar to str/bytes relationship), providing:

- Precise Decimal-based calculations for accuracy
- Immutable, strongly-typed color representations
- WCAG contrast calculations and adjustments
- Support for multiple color space encodings

Example usage:
    from bukzor_color import Color, HexEncoding, RGBEncoding
    from bukzor_color import calculate_contrast, adjust_contrast

    # Parse any color format
    color = HexEncoding.parse("#ff0000").decode()

    # Or use auto-detection
    from bukzor_color import auto_parse
    color = auto_parse("rgb(255, 0, 0)").decode()

    # Convert between formats
    hex_enc = color.encode(HexEncoding)
    rgb_enc = color.encode(RGBEncoding)

    # Type-safe contrast operations
    fg = auto_parse("#333").decode()
    bg = auto_parse("#eee").decode()

    result = calculate_contrast(fg, bg)
    if not result.passes_AA:
        new_fg, new_bg, new_result = adjust_contrast(fg, bg, "AA")
"""

# Core color model
from bukzor_color.core import Color as Color
from bukzor_color.core import ColorWithAlpha as ColorWithAlpha

# Color encodings
from bukzor_color.encodings import encodings

ColorEncoding = encodings.ColorEncoding
HexEncoding = encodings.HexEncoding
WcagHCLEncoding = encodings.WcagHCLEncoding
auto_parse = encodings.auto_parse

# Contrast calculations
from bukzor_color.contrast import ContrastResult as ContrastResult
from bukzor_color.contrast import adjust_contrast as adjust_contrast
from bukzor_color.contrast import calculate_contrast as calculate_contrast
from bukzor_color.contrast import get_target_ratio as get_target_ratio

# Type definitions
from bukzor_color.types import AdjustTarget as AdjustTarget
from bukzor_color.types import ColorSpace as ColorSpace
from bukzor_color.types import ContrastRatio as ContrastRatio
from bukzor_color.types import Luminance as Luminance
from bukzor_color.types import WCAGLevel as WCAGLevel

__version__ = "0.1.0"
