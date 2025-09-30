"""Hex color encoding."""

import re
from dataclasses import dataclass
from typing import Self

from bukzor_color.core import Color
from bukzor_color.encodings.base import ColorEncoding
from bukzor_color.types import RGBChannel


@dataclass(frozen=True, slots=True)
class HexEncoding(ColorEncoding):
    """Hex color encoding like '#ff0000'."""

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
        """Parse text to hex encoding."""
        # Normalize format
        clean_text = text.strip()
        if clean_text.startswith("#"):
            clean_text = clean_text[1:]

        # Expand 3-character hex to 6-character
        if re.match(r"^[0-9a-fA-F]{3}$", clean_text):
            # abc -> aabbcc
            expanded = "".join(c * 2 for c in clean_text)
            clean_text = expanded

        if not re.match(r"^[0-9a-fA-F]{6}$", clean_text):
            raise ValueError(f"Invalid hex format: {text}")

        # Parse to RGB components
        hex_value = int(clean_text, 16)
        r = (hex_value >> 16) & 0xFF
        g = (hex_value >> 8) & 0xFF
        b = hex_value & 0xFF

        return cls(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    def __str__(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
