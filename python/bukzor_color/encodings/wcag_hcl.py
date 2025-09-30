"""WCAG HCL color encoding."""

import math
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from bukzor_color.core import Color
from bukzor_color.encodings.base import ColorEncoding
from bukzor_color.types import Degrees, Percentage, Luminance



# WCAG luminance coefficients (the third axis)
_WCAG_R = Decimal('0.2126')
_WCAG_G = Decimal('0.7152')
_WCAG_B = Decimal('0.0722')

# Precomputed orthogonal basis vectors for chromaticity projection
# u1: Red-Green axis (perpendicular to luminance vector)
_U1_R = Decimal('0.958546')
_U1_G = Decimal('-0.284937')
_U1_B = Decimal('0')

# u2: Blue-Yellow axis (perpendicular to both luminance and u1)
_U2_R = Decimal('0.027444')
_U2_G = Decimal('0.092323')
_U2_B = Decimal('-0.995351')


@dataclass(frozen=True, slots=True)
class WcagHCLEncoding(ColorEncoding):
    """HCL encoding where L is WCAG luminance (not perceptual lightness)."""

    h: Degrees
    c: Percentage
    l: Luminance

    def decode(self) -> Color:
        """Decode this encoding to a Color."""
        if self.c == 0:
            # Clamp luminance to [0,1] range for achromatic colors
            clamped_l = max(Decimal('0'), min(Decimal('1'), self.l))
            return Color.from_linear_rgb(clamped_l, clamped_l, clamped_l)

        # Convert hue to unit vector in chromaticity plane
        h_rad = self.h * Decimal(str(math.pi)) / Decimal('180')
        unit_x = Decimal(str(math.cos(float(h_rad))))
        unit_y = Decimal(str(math.sin(float(h_rad))))

        # Convert to RGB direction using basis vectors
        dir_r = unit_x * _U1_R + unit_y * _U2_R
        dir_g = unit_x * _U1_G + unit_y * _U2_G
        dir_b = unit_x * _U1_B + unit_y * _U2_B

        # Find maximum scale at this H and L
        max_scale = Decimal('inf')
        for gray_val, dir_val in [(self.l, dir_r), (self.l, dir_g), (self.l, dir_b)]:
            if dir_val > 0:
                max_scale = min(max_scale, (Decimal('1') - gray_val) / dir_val)
            elif dir_val < 0:
                max_scale = min(max_scale, -gray_val / dir_val)

        # Apply chroma as percentage of maximum
        actual_scale = max_scale * (self.c / Decimal('100'))

        # Calculate final RGB and clamp to [0,1] range
        r = max(Decimal('0'), min(Decimal('1'), self.l + actual_scale * dir_r))
        g = max(Decimal('0'), min(Decimal('1'), self.l + actual_scale * dir_g))
        b = max(Decimal('0'), min(Decimal('1'), self.l + actual_scale * dir_b))

        return Color.from_linear_rgb(r, g, b)

    @classmethod
    def encode(cls, color: Color) -> Self:
        """Encode a Color to this encoding format."""
        # WCAG luminance (exact as specified)
        L = _WCAG_R * color.red + _WCAG_G * color.green + _WCAG_B * color.blue

        # Chroma vector (distance from gray axis)
        chroma_r = color.red - L
        chroma_g = color.green - L
        chroma_b = color.blue - L

        # Project chroma vector onto orthogonal basis vectors
        x = chroma_r * _U1_R + chroma_g * _U1_G + chroma_b * _U1_B
        y = chroma_r * _U2_R + chroma_g * _U2_G + chroma_b * _U2_B

        # Calculate hue and chroma magnitude
        if x == 0 and y == 0:
            return cls(Degrees(Decimal('0')), Percentage(Decimal('0')), Luminance(L))

        H = (Decimal(str(math.atan2(float(y), float(x)))) * Decimal('180') / Decimal(str(math.pi))) % Decimal('360')
        chroma_magnitude = (x**2 + y**2).sqrt()

        # Find maximum chroma at this H and L
        cos_H = x / chroma_magnitude
        sin_H = y / chroma_magnitude

        # Convert to RGB direction
        dir_r = cos_H * _U1_R + sin_H * _U2_R
        dir_g = cos_H * _U1_G + sin_H * _U2_G
        dir_b = cos_H * _U1_B + sin_H * _U2_B

        # Find maximum scale before hitting RGB boundaries [0,1]
        max_scale = Decimal('inf')
        for gray_val, dir_val in [(L, dir_r), (L, dir_g), (L, dir_b)]:
            if dir_val > 0:
                max_scale = min(max_scale, (Decimal('1') - gray_val) / dir_val)
            elif dir_val < 0:
                max_scale = min(max_scale, -gray_val / dir_val)

        # Normalize chroma as percentage of maximum
        C = (chroma_magnitude / max_scale * Decimal('100')) if max_scale > 0 and max_scale != Decimal('inf') else Decimal('0')

        return cls(Degrees(H), Percentage(C), Luminance(L))

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse text to WCAG HCL encoding."""
        text = text.strip()

        # Parse "wcag-hcl(h, c%, l)" format
        match = re.match(r'wcag-hcl\(\s*([0-9.]+)\s*,\s*([0-9.]+)%?\s*,\s*([0-9.]+)\s*\)', text)
        if not match:
            raise ValueError(f"Invalid wcag-hcl format: {text}")

        h = Decimal(match.group(1))
        c = Decimal(match.group(2))
        l = Decimal(match.group(3))

        return cls(Degrees(h), Percentage(c), Luminance(l))

    def __str__(self) -> str:
        return f"wcag-hcl({self.h:.0f}, {self.c:.0f}%, {self.l:.3f})"

