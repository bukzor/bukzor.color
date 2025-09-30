"""HSL color encoding."""

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from bukzor_color.core import Color
from bukzor_color.encodings.base import ColorEncoding
from bukzor_color.types import HSLHue, HSLSaturation, HSLLightness


@dataclass(frozen=True, slots=True)
class HSLEncoding(ColorEncoding):
    """HSL color encoding like 'hsl(0, 100%, 50%)'."""

    h: HSLHue
    s: HSLSaturation
    l: HSLLightness

    def decode(self) -> Color:
        """Decode this encoding to a Color."""
        return Color.from_hsl(self.h, self.s, self.l)

    @classmethod
    def encode(cls, color: Color) -> Self:
        """Encode a Color to this encoding format."""
        h, s, l = color.to_hsl()
        return cls(HSLHue(h), HSLSaturation(s), HSLLightness(l))

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse text to HSL encoding."""
        text = text.strip()

        # Parse "hsl(h, s%, l%)" format
        match = re.match(r'hsl\(\s*([0-9.]+)\s*,\s*([0-9.]+)%?\s*,\s*([0-9.]+)%?\s*\)', text)
        if not match:
            raise ValueError(f"Invalid HSL format: {text}")

        h = Decimal(match.group(1))
        s = Decimal(match.group(2))
        l = Decimal(match.group(3))

        # Validate ranges
        if not 0 <= h <= 360:
            raise ValueError(f"HSL hue must be 0-360, got {h}")
        if not 0 <= s <= 100:
            raise ValueError(f"HSL saturation must be 0-100, got {s}")
        if not 0 <= l <= 100:
            raise ValueError(f"HSL lightness must be 0-100, got {l}")

        return cls(HSLHue(h), HSLSaturation(s), HSLLightness(l))

    def __str__(self) -> str:
        return f"hsl({self.h:.0f}, {self.s:.0f}%, {self.l:.0f}%)"