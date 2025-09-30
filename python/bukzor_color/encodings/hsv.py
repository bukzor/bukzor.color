"""HSV color encoding."""

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from bukzor_color.core import Color
from bukzor_color.encodings.base import ColorEncoding
from bukzor_color.types import HSVHue
from bukzor_color.types import HSVSaturation
from bukzor_color.types import HSVValue


@dataclass(frozen=True, slots=True)
class HSVEncoding(ColorEncoding):
    """HSV color encoding like 'hsv(0, 100%, 100%)'."""

    h: HSVHue
    s: HSVSaturation
    v: HSVValue

    def decode(self) -> Color:
        """Decode this encoding to a Color."""
        return Color.from_hsv(self.h, self.s, self.v)

    @classmethod
    def encode(cls, color: Color) -> Self:
        """Encode a Color to this encoding format."""
        h, s, v = color.to_hsv()
        return cls(HSVHue(h), HSVSaturation(s), HSVValue(v))

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse text to HSV encoding."""
        text = text.strip()

        # Parse "hsv(h, s%, v%)" format
        match = re.match(
            r"hsv\(\s*([0-9.]+)\s*,\s*([0-9.]+)%?\s*,\s*([0-9.]+)%?\s*\)", text
        )
        if not match:
            raise ValueError(f"Invalid HSV format: {text}")

        h = Decimal(match.group(1))
        s = Decimal(match.group(2))
        v = Decimal(match.group(3))

        # Validate ranges
        if not 0 <= h <= 360:
            raise ValueError(f"HSV hue must be 0-360, got {h}")
        if not 0 <= s <= 100:
            raise ValueError(f"HSV saturation must be 0-100, got {s}")
        if not 0 <= v <= 100:
            raise ValueError(f"HSV value must be 0-100, got {v}")

        return cls(HSVHue(h), HSVSaturation(s), HSVValue(v))

    def __str__(self) -> str:
        return f"hsv({self.h:.0f}, {self.s:.0f}%, {self.v:.0f}%)"
