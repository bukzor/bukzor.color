"""Immutable color models using frozen dataclasses."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from bukzor_color.types import (
    ContrastRatio,
    HSLHue,
    HSLLightness,
    HSLSaturation,
    HSVHue,
    HSVSaturation,
    HSVValue,
    Luminance,
    RGBChannel,
    Ratio,
)


@dataclass(frozen=True, slots=True)
class RGB:
    """Immutable RGB color in sRGB color space."""

    r: RGBChannel
    g: RGBChannel
    b: RGBChannel

    def __post_init__(self) -> None:
        """Validate RGB values are in valid range."""
        for channel, value in [("r", self.r), ("g", self.g), ("b", self.b)]:
            if not 0 <= value <= 255:
                raise ValueError(f"RGB {channel} must be 0-255, got {value}")

    @classmethod
    def from_hex(cls, hex_string: str) -> Self:
        """Parse from hex string like '#ff0000' or 'ff0000'."""
        # Remove # if present and validate format
        hex_clean = hex_string.lstrip("#")
        if not re.match(r"^[0-9a-fA-F]{6}$", hex_clean):
            raise ValueError(f"Invalid hex color format: {hex_string}")

        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)

        return cls(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    @classmethod
    def from_rgb_string(cls, rgb_string: str) -> Self:
        """Parse from rgb string like 'rgb(255, 0, 0)'."""
        # Extract numbers from rgb() format
        match = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", rgb_string)
        if not match:
            raise ValueError(f"Invalid RGB format: {rgb_string}")

        r, g, b = map(int, match.groups())
        return cls(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    def to_hex(self) -> str:
        """Convert to lowercase hex string like '#ff0000'."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb_string(self) -> str:
        """Convert to RGB string like 'rgb(255, 0, 0)'."""
        return f"rgb({self.r}, {self.g}, {self.b})"

    def luminance(self) -> Luminance:
        """Calculate relative luminance per WCAG 2.1."""
        # Convert to linear RGB using Decimal for precision
        def linearize(channel: int) -> Decimal:
            normalized = Decimal(channel) / Decimal('255')
            if normalized <= Decimal('0.03928'):
                return normalized / Decimal('12.92')
            else:
                return ((normalized + Decimal('0.055')) / Decimal('1.055')) ** Decimal('2.4')

        r_linear = linearize(self.r)
        g_linear = linearize(self.g)
        b_linear = linearize(self.b)

        # ITU-R BT.709 coefficients
        return Luminance(
            Decimal('0.2126') * r_linear +
            Decimal('0.7152') * g_linear +
            Decimal('0.0722') * b_linear
        )

    def contrast_ratio(self, other: RGB) -> ContrastRatio:
        """Calculate WCAG contrast ratio with another color."""
        l1 = self.luminance()
        l2 = other.luminance()

        # Ensure lighter color is in numerator
        if l1 > l2:
            return ContrastRatio((l1 + Decimal('0.05')) / (l2 + Decimal('0.05')))
        else:
            return ContrastRatio((l2 + Decimal('0.05')) / (l1 + Decimal('0.05')))

    def with_alpha(self, alpha: Ratio) -> RGBA:
        """Create RGBA color with alpha channel."""
        return RGBA(self.r, self.g, self.b, alpha)

    def to_hsl(self) -> HSL:
        """Convert to HSL color space."""
        r_norm = Decimal(self.r) / Decimal('255')
        g_norm = Decimal(self.g) / Decimal('255')
        b_norm = Decimal(self.b) / Decimal('255')

        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val

        # Lightness
        lightness = (max_val + min_val) / Decimal('2')

        if diff == 0:
            # Achromatic (gray)
            hue = Decimal('0')
            saturation = Decimal('0')
        else:
            # Saturation
            if lightness < Decimal('0.5'):
                saturation = diff / (max_val + min_val)
            else:
                saturation = diff / (Decimal('2') - max_val - min_val)

            # Hue
            if max_val == r_norm:
                hue = (g_norm - b_norm) / diff
                if g_norm < b_norm:
                    hue += Decimal('6')
            elif max_val == g_norm:
                hue = (b_norm - r_norm) / diff + Decimal('2')
            else:  # max_val == b_norm
                hue = (r_norm - g_norm) / diff + Decimal('4')

            hue *= Decimal('60')  # Convert to degrees

        return HSL(
            HSLHue(hue),
            HSLSaturation(saturation * Decimal('100')),
            HSLLightness(lightness * Decimal('100')),
        )

    def to_hsv(self) -> HSV:
        """Convert to HSV color space."""
        r_norm: float = self.r / 255.0
        g_norm: float = self.g / 255.0
        b_norm: float = self.b / 255.0

        max_val: float = max(r_norm, g_norm, b_norm)
        min_val: float = min(r_norm, g_norm, b_norm)
        diff: float = max_val - min_val

        # Value
        value: float = max_val

        # Saturation
        if max_val == 0:
            saturation: float = 0.0
        else:
            saturation = diff / max_val

        # Hue
        if diff == 0:
            hue: float = 0.0
        else:
            if max_val == r_norm:
                hue = (g_norm - b_norm) / diff
                if g_norm < b_norm:
                    hue += 6.0
            elif max_val == g_norm:
                hue = (b_norm - r_norm) / diff + 2.0
            else:  # max_val == b_norm
                hue = (r_norm - g_norm) / diff + 4.0

            hue *= 60.0  # Convert to degrees

        return HSV(
            HSVHue(Decimal(str(hue))),
            HSVSaturation(Decimal(str(saturation * 100.0))),
            HSVValue(Decimal(str(value * 100.0))),
        )


@dataclass(frozen=True, slots=True)
class RGBA:
    """Immutable RGBA color with alpha channel."""

    r: RGBChannel
    g: RGBChannel
    b: RGBChannel
    a: Ratio

    def __post_init__(self) -> None:
        """Validate RGBA values are in valid range."""
        for channel, value in [("r", self.r), ("g", self.g), ("b", self.b)]:
            if not 0 <= value <= 255:
                raise ValueError(f"RGB {channel} must be 0-255, got {value}")
        if not 0 <= self.a <= 1:
            raise ValueError(f"Alpha must be 0.0-1.0, got {self.a}")

    def opaque(self) -> RGB:
        """Remove alpha channel."""
        return RGB(self.r, self.g, self.b)

    def over(self, background: RGB) -> RGB:
        """Composite over background using alpha blending."""
        # Alpha compositing formula: C = αA + (1-α)B
        alpha = self.a
        inv_alpha = Decimal('1.0') - alpha

        r = int(alpha * self.r + inv_alpha * background.r)
        g = int(alpha * self.g + inv_alpha * background.g)
        b = int(alpha * self.b + inv_alpha * background.b)

        return RGB(RGBChannel(r), RGBChannel(g), RGBChannel(b))

    def to_rgba_string(self) -> str:
        """Convert to RGBA string like 'rgba(255, 0, 0, 0.5)'."""
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"


@dataclass(frozen=True, slots=True)
class HSL:
    """Immutable HSL color representation."""

    h: HSLHue  # 0-360 degrees
    s: HSLSaturation  # 0-100 percentage
    l: HSLLightness  # 0-100 percentage

    def __post_init__(self) -> None:
        """Validate HSL values are in valid range."""
        if not 0 <= self.h < 360:
            raise ValueError(f"HSL hue must be 0-359.99, got {self.h}")
        if not 0 <= self.s <= 100:
            raise ValueError(f"HSL saturation must be 0-100, got {self.s}")
        if not 0 <= self.l <= 100:
            raise ValueError(f"HSL lightness must be 0-100, got {self.l}")

    @classmethod
    def from_hsl_string(cls, hsl_string: str) -> Self:
        """Parse from HSL string like 'hsl(240, 100%, 50%)'."""
        match = re.match(
            r"hsl\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*\)",
            hsl_string,
        )
        if not match:
            raise ValueError(f"Invalid HSL format: {hsl_string}")

        h, s, l = map(Decimal, match.groups())
        return cls(HSLHue(h), HSLSaturation(s), HSLLightness(l))

    def to_hsl_string(self) -> str:
        """Convert to HSL string like 'hsl(240, 100%, 50%)'."""
        return f"hsl({self.h:.0f}, {self.s:.0f}%, {self.l:.0f}%)"

    def to_rgb(self) -> RGB:
        """Convert to RGB color space."""
        h_norm = self.h / Decimal('360.0')
        s_norm = self.s / Decimal('100.0')
        l_norm = self.l / Decimal('100.0')

        if s_norm == 0:
            # Achromatic (gray)
            gray: int = int(l_norm * Decimal('255'))
            return RGB(RGBChannel(gray), RGBChannel(gray), RGBChannel(gray))

        def hue_to_rgb(p: Decimal, q: Decimal, t: Decimal) -> Decimal:
            if t < 0:
                t += Decimal('1')
            if t > 1:
                t -= Decimal('1')
            if t < Decimal('1') / Decimal('6'):
                return p + (q - p) * Decimal('6') * t
            if t < Decimal('1') / Decimal('2'):
                return q
            if t < Decimal('2') / Decimal('3'):
                return p + (q - p) * (Decimal('2') / Decimal('3') - t) * Decimal('6')
            return p

        if l_norm < Decimal('0.5'):
            q = l_norm * (Decimal('1') + s_norm)
        else:
            q = l_norm + s_norm - l_norm * s_norm

        p = Decimal('2') * l_norm - q

        r = hue_to_rgb(p, q, h_norm + Decimal('1') / Decimal('3'))
        g = hue_to_rgb(p, q, h_norm)
        b = hue_to_rgb(p, q, h_norm - Decimal('1') / Decimal('3'))

        return RGB(
            RGBChannel(int(round(r * Decimal('255')))),
            RGBChannel(int(round(g * Decimal('255')))),
            RGBChannel(int(round(b * Decimal('255')))),
        )

    def with_lightness(self, lightness: HSLLightness) -> Self:
        """Create new HSL with different lightness."""
        return self.__class__(self.h, self.s, lightness)

    def with_saturation(self, saturation: HSLSaturation) -> Self:
        """Create new HSL with different saturation."""
        return self.__class__(self.h, saturation, self.l)

    def with_hue(self, hue: HSLHue) -> Self:
        """Create new HSL with different hue."""
        return self.__class__(hue, self.s, self.l)


@dataclass(frozen=True, slots=True)
class HSV:
    """Immutable HSV color representation."""

    h: HSVHue  # 0-360 degrees
    s: HSVSaturation  # 0-100 percentage
    v: HSVValue  # 0-100 percentage

    def __post_init__(self) -> None:
        """Validate HSV values are in valid range."""
        if not 0.0 <= self.h < 360.0:
            raise ValueError(f"HSV hue must be 0-359.99, got {self.h}")
        if not 0.0 <= self.s <= 100.0:
            raise ValueError(f"HSV saturation must be 0-100, got {self.s}")
        if not 0.0 <= self.v <= 100.0:
            raise ValueError(f"HSV value must be 0-100, got {self.v}")

    @classmethod
    def from_hsv_string(cls, hsv_string: str) -> Self:
        """Parse from HSV string like 'hsv(240, 100%, 50%)'."""
        match = re.match(
            r"hsv\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*\)",
            hsv_string,
        )
        if not match:
            raise ValueError(f"Invalid HSV format: {hsv_string}")

        h, s, v = map(Decimal, match.groups())
        return cls(HSVHue(h), HSVSaturation(s), HSVValue(v))

    def to_hsv_string(self) -> str:
        """Convert to HSV string like 'hsv(240, 100%, 50%)'."""
        return f"hsv({self.h:.0f}, {self.s:.0f}%, {self.v:.0f}%)"

    def to_rgb(self) -> RGB:
        """Convert to RGB color space."""
        h_norm = self.h / Decimal('360.0')
        s_norm = self.s / Decimal('100.0')
        v_norm = self.v / Decimal('100.0')

        if s_norm == 0:
            # Achromatic (gray)
            gray: int = int(v_norm * Decimal('255'))
            return RGB(RGBChannel(gray), RGBChannel(gray), RGBChannel(gray))

        h_sector = h_norm * Decimal('6.0')
        i = int(h_sector)
        f = h_sector - Decimal(i)

        p = v_norm * (Decimal('1') - s_norm)
        q = v_norm * (Decimal('1') - s_norm * f)
        t = v_norm * (Decimal('1') - s_norm * (Decimal('1') - f))

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

        return RGB(
            RGBChannel(int(round(r * Decimal('255')))),
            RGBChannel(int(round(g * Decimal('255')))),
            RGBChannel(int(round(b * Decimal('255')))),
        )

    def with_value(self, value: HSVValue) -> Self:
        """Create new HSV with different value."""
        return self.__class__(self.h, self.s, value)

    def with_saturation(self, saturation: HSVSaturation) -> Self:
        """Create new HSV with different saturation."""
        return self.__class__(self.h, saturation, self.v)

    def with_hue(self, hue: HSVHue) -> Self:
        """Create new HSV with different hue."""
        return self.__class__(hue, self.s, self.v)