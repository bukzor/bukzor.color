"""RGB color encoding."""

import re
from dataclasses import dataclass
from typing import Self

from bukzor_color.core import Color
from bukzor_color.encodings.base import ColorEncoding
from bukzor_color.types import RGBChannel


@dataclass(frozen=True, slots=True)
class RGBEncoding(ColorEncoding):
    """RGB color encoding like 'rgb(255, 0, 0)'."""

    r: RGBChannel
    g: RGBChannel
    b: RGBChannel

    def decode(self) -> Color:
        """Decode this encoding to a Color."""
        return Color.from_srgb(self.r, self.g, self.b)

    @classmethod
    def encode(cls, color: Color) -> Self:
        """Encode a Color to this encoding format."""
        r, g, b = color.to_srgb()
        return cls(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse text to RGB encoding."""
        text = text.strip()

        # Parse "rgb(r, g, b)" format
        match = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text)
        if not match:
            raise ValueError(f"Invalid RGB format: {text}")

        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))

        # Validate range
        for component, value in [("red", r), ("green", g), ("blue", b)]:
            if not 0 <= value <= 255:
                raise ValueError(f"RGB {component} must be 0-255, got {value}")

        return cls(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    def __str__(self) -> str:
        return f"rgb({self.r}, {self.g}, {self.b})"
