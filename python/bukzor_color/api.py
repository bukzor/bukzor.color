"""Universal Color API with lazy conversion and comprehensive parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field
from decimal import Decimal
from typing import Self

from bukzor_color.models import HSL
from bukzor_color.models import HSV
from bukzor_color.models import RGB
from bukzor_color.models import RGBA
from bukzor_color.types import ColorSpace


@dataclass(frozen=True, slots=True)
class Color:
    """
    Universal color container with lazy conversion.
    Stores original format and converts on demand.
    """

    _rgb: RGB | None = field(default=None, repr=False)
    _hsl: HSL | None = field(default=None, repr=False)
    _hsv: HSV | None = field(default=None, repr=False)
    _original_format: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        """Ensure at least one color representation is provided."""
        if not any([self._rgb, self._hsl, self._hsv]):
            raise ValueError(
                "At least one color representation must be provided"
            )

    @classmethod
    def from_rgb(cls, rgb: RGB) -> Self:
        """Create Color from RGB."""
        return cls(_rgb=rgb, _original_format="rgb")

    @classmethod
    def from_hsl(cls, hsl: HSL) -> Self:
        """Create Color from HSL."""
        return cls(_hsl=hsl, _original_format="hsl")

    @classmethod
    def from_hsv(cls, hsv: HSV) -> Self:
        """Create Color from HSV."""
        return cls(_hsv=hsv, _original_format="hsv")

    @classmethod
    def parse(cls, color_string: str) -> Self:
        """Parse any supported color format."""
        color_string = color_string.strip()

        # Try hex format first
        if _is_hex_color(color_string):
            rgb = RGB.from_hex(color_string)
            return cls.from_rgb(rgb)

        # Try rgb() format
        if color_string.startswith("rgb("):
            rgb = RGB.from_rgb_string(color_string)
            return cls.from_rgb(rgb)

        # Try hsl() format
        if color_string.startswith("hsl("):
            hsl = HSL.from_hsl_string(color_string)
            return cls.from_hsl(hsl)

        # Try hsv() format
        if color_string.startswith("hsv("):
            hsv = HSV.from_hsv_string(color_string)
            return cls.from_hsv(hsv)

        # Try CSS named colors
        if color_string.lower() in CSS_NAMED_COLORS:
            hex_value = CSS_NAMED_COLORS[color_string.lower()]
            rgb = RGB.from_hex(hex_value)
            return cls.from_rgb(rgb)

        raise ValueError(f"Unrecognized color format: {color_string}")

    @property
    def rgb(self) -> RGB:
        """Get RGB representation, converting if needed."""
        if self._rgb is not None:
            return self._rgb

        if self._hsl is not None:
            # Convert from HSL
            rgb = self._hsl.to_rgb()
            # Cache the result for future access
            object.__setattr__(self, "_rgb", rgb)
            return rgb

        if self._hsv is not None:
            # Convert from HSV
            rgb = self._hsv.to_rgb()
            # Cache the result for future access
            object.__setattr__(self, "_rgb", rgb)
            return rgb

        # Should never reach here due to __post_init__ validation
        raise RuntimeError("No color representation available")

    @property
    def hsl(self) -> HSL:
        """Get HSL representation, converting if needed."""
        if self._hsl is not None:
            return self._hsl

        # Convert from RGB
        hsl = self.rgb.to_hsl()
        # Cache the result for future access
        object.__setattr__(self, "_hsl", hsl)
        return hsl

    @property
    def hsv(self) -> HSV:
        """Get HSV representation, converting if needed."""
        if self._hsv is not None:
            return self._hsv

        # Convert from RGB
        hsv = self.rgb.to_hsv()
        # Cache the result for future access
        object.__setattr__(self, "_hsv", hsv)
        return hsv

    def in_space(self, space: ColorSpace) -> RGB | HSL | HSV:
        """Get color in specified space."""
        if space == "rgb":
            return self.rgb
        elif space == "hsl":
            return self.hsl
        elif space == "hsv":
            return self.hsv
        else:
            raise ValueError(f"Unsupported color space: {space}")

    def to_hex(self) -> str:
        """Convert to hex string."""
        return self.rgb.to_hex()

    def to_rgb_string(self) -> str:
        """Convert to RGB string."""
        return self.rgb.to_rgb_string()

    def to_hsl_string(self) -> str:
        """Convert to HSL string."""
        return self.hsl.to_hsl_string()

    def to_hsv_string(self) -> str:
        """Convert to HSV string."""
        return self.hsv.to_hsv_string()

    def with_alpha(self, alpha: float | Decimal) -> ColorWithAlpha:
        """Add alpha channel."""
        from decimal import Decimal

        from bukzor_color.types import Ratio

        if isinstance(alpha, float):
            alpha = Decimal(str(alpha))
        elif isinstance(alpha, int):
            alpha = Decimal(alpha)
        return ColorWithAlpha(self, Ratio(alpha))

    def __str__(self) -> str:
        """String representation using original format when possible."""
        if self._original_format == "hsl" and self._hsl is not None:
            return self.to_hsl_string()
        elif self._original_format == "hsv" and self._hsv is not None:
            return self.to_hsv_string()
        else:
            return self.to_hex()


@dataclass(frozen=True, slots=True)
class ColorWithAlpha:
    """Color with alpha channel for transparency support."""

    color: Color
    alpha: Decimal

    def __post_init__(self) -> None:
        """Validate alpha value."""
        if not 0 <= self.alpha <= 1:
            raise ValueError(f"Alpha must be 0.0-1.0, got {self.alpha}")

    @property
    def rgba(self) -> RGBA:
        """Get RGBA representation."""
        from bukzor_color.types import Ratio

        return self.color.rgb.with_alpha(Ratio(self.alpha))

    def over(self, background: Color) -> Color:
        """Composite over background color."""
        composited = self.rgba.over(background.rgb)
        return Color.from_rgb(composited)


def _is_hex_color(color_string: str) -> bool:
    """Check if string is a valid hex color."""
    hex_clean = color_string.lstrip("#")
    return bool(re.match(r"^[0-9a-fA-F]{6}$", hex_clean))


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
