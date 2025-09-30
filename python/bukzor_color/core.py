"""Core color representation independent of encoding format."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from bukzor_color.encodings.base import ColorEncoding



@dataclass(frozen=True, slots=True)
class Color:
    """
    A color as an abstract concept, independent of representation.

    Internally stores as linear RGB in [0,1] range for maximum precision
    and to avoid encoding-specific artifacts. All representations are
    computed from this canonical form.
    """

    # Linear RGB components in [0,1] range using Decimal for precision
    red: Decimal    # Linear red component 0-1
    green: Decimal  # Linear green component 0-1
    blue: Decimal   # Linear blue component 0-1

    def __post_init__(self) -> None:
        """Validate color components are in valid range."""
        for component, value in [("red", self.red), ("green", self.green), ("blue", self.blue)]:
            if not 0 <= value <= 1:
                raise ValueError(f"Color {component} must be 0-1, got {value}")


    def _validate_for_egress(self) -> None:
        """Validate color components before output/conversion."""
        for component, value in [("red", self.red), ("green", self.green), ("blue", self.blue)]:
            if not 0 <= value <= 1:
                raise ValueError(f"Color {component} must be 0-1 for output, got {value}")

    @classmethod
    def from_linear_rgb(cls, r: Decimal, g: Decimal, b: Decimal) -> Self:
        """Create color from linear RGB values in [0,1] range."""
        return cls(r, g, b)

    @classmethod
    def from_srgb(cls, r: int, g: int, b: int) -> Self:
        """Create color from sRGB values in [0,255] range."""
        # Convert sRGB to linear RGB
        def srgb_to_linear(channel: int) -> Decimal:
            normalized = Decimal(channel) / Decimal('255')
            if normalized <= Decimal('0.04045'):
                return normalized / Decimal('12.92')
            else:
                return ((normalized + Decimal('0.055')) / Decimal('1.055')) ** Decimal('2.4')

        return cls(
            srgb_to_linear(r),
            srgb_to_linear(g),
            srgb_to_linear(b)
        )

    @classmethod
    def from_hex(cls, hex_string: str) -> Self:
        """Create color from hex string like '#ff0000'."""
        import re

        hex_clean = hex_string.lstrip("#")
        if not re.match(r"^[0-9a-fA-F]{6}$", hex_clean):
            raise ValueError(f"Invalid hex color format: {hex_string}")

        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)

        return cls.from_srgb(r, g, b)

    @classmethod
    def from_hsl(cls, h: Decimal, s: Decimal, l: Decimal) -> Self:
        """Create color from HSL values (h: 0-360, s,l: 0-100)."""
        h_norm = h / Decimal('360')
        s_norm = s / Decimal('100')
        l_norm = l / Decimal('100')

        if s_norm == 0:
            # Achromatic
            r = g = b = l_norm
        else:
            def hue_to_rgb(p: Decimal, q: Decimal, t: Decimal) -> Decimal:
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < Decimal('1') / 6:
                    return p + (q - p) * 6 * t
                if t < Decimal('1') / 2:
                    return q
                if t < Decimal('2') / 3:
                    return p + (q - p) * (Decimal('2') / 3 - t) * 6
                return p

            if l_norm < Decimal('0.5'):
                q = l_norm * (1 + s_norm)
            else:
                q = l_norm + s_norm - l_norm * s_norm

            p = 2 * l_norm - q

            r = hue_to_rgb(p, q, h_norm + Decimal('1') / 3)
            g = hue_to_rgb(p, q, h_norm)
            b = hue_to_rgb(p, q, h_norm - Decimal('1') / 3)

        # Convert sRGB to linear
        def srgb_to_linear(component: Decimal) -> Decimal:
            if component <= Decimal('0.04045'):
                return component / Decimal('12.92')
            else:
                return ((component + Decimal('0.055')) / Decimal('1.055')) ** Decimal('2.4')

        return cls(
            srgb_to_linear(r),
            srgb_to_linear(g),
            srgb_to_linear(b)
        )

    @classmethod
    def from_hsv(cls, h: Decimal, s: Decimal, v: Decimal) -> Self:
        """Create color from HSV values (h: 0-360, s,v: 0-100)."""
        h_norm = h / Decimal('360')
        s_norm = s / Decimal('100')
        v_norm = v / Decimal('100')

        if s_norm == 0:
            # Achromatic
            r = g = b = v_norm
        else:
            h_sector = int(h_norm * 6) % 6
            h_fract = (h_norm * 6) - h_sector

            p = v_norm * (1 - s_norm)
            q = v_norm * (1 - s_norm * h_fract)
            t = v_norm * (1 - s_norm * (1 - h_fract))

            if h_sector == 0:
                r, g, b = v_norm, t, p
            elif h_sector == 1:
                r, g, b = q, v_norm, p
            elif h_sector == 2:
                r, g, b = p, v_norm, t
            elif h_sector == 3:
                r, g, b = p, q, v_norm
            elif h_sector == 4:
                r, g, b = t, p, v_norm
            else:  # h_sector == 5
                r, g, b = v_norm, p, q

        # Convert sRGB to linear
        def srgb_to_linear(component: Decimal) -> Decimal:
            if component <= Decimal('0.04045'):
                return component / Decimal('12.92')
            else:
                return ((component + Decimal('0.055')) / Decimal('1.055')) ** Decimal('2.4')

        return cls(
            srgb_to_linear(r),
            srgb_to_linear(g),
            srgb_to_linear(b)
        )

    def to_srgb(self) -> tuple[int, int, int]:
        """Convert to sRGB values in [0,255] range."""
        def linear_to_srgb(component: Decimal) -> int:
            if component <= Decimal('0.0031308'):
                srgb = component * Decimal('12.92')
            else:
                srgb = Decimal('1.055') * (component ** (Decimal('1') / Decimal('2.4'))) - Decimal('0.055')

            # Clamp and convert to int
            return max(0, min(255, int(srgb * 255 + Decimal('0.5'))))

        return (
            linear_to_srgb(self.red),
            linear_to_srgb(self.green),
            linear_to_srgb(self.blue)
        )

    def to_hex(self) -> str:
        """Convert to hex string like '#ff0000'."""
        r, g, b = self.to_srgb()
        return f"#{r:02x}{g:02x}{b:02x}"

    def to_hsl(self) -> tuple[Decimal, Decimal, Decimal]:
        """Convert to HSL values (h: 0-360, s,l: 0-100)."""
        # First convert to sRGB for HSL calculation
        def linear_to_srgb_norm(component: Decimal) -> Decimal:
            if component <= Decimal('0.0031308'):
                return component * Decimal('12.92')
            else:
                return Decimal('1.055') * (component ** (Decimal('1') / Decimal('2.4'))) - Decimal('0.055')

        r_norm = linear_to_srgb_norm(self.red)
        g_norm = linear_to_srgb_norm(self.green)
        b_norm = linear_to_srgb_norm(self.blue)

        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val

        # Lightness
        lightness = (max_val + min_val) / 2

        if diff == 0:
            # Achromatic
            hue = Decimal('0')
            saturation = Decimal('0')
        else:
            # Saturation
            if lightness < Decimal('0.5'):
                saturation = diff / (max_val + min_val)
            else:
                saturation = diff / (2 - max_val - min_val)

            # Hue
            if max_val == r_norm:
                hue = (g_norm - b_norm) / diff
                if g_norm < b_norm:
                    hue += 6
            elif max_val == g_norm:
                hue = (b_norm - r_norm) / diff + 2
            else:  # max_val == b_norm
                hue = (r_norm - g_norm) / diff + 4

            hue *= 60  # Convert to degrees

        return (hue, saturation * 100, lightness * 100)

    def to_hsv(self) -> tuple[Decimal, Decimal, Decimal]:
        """Convert to HSV values (h: 0-360, s,v: 0-100)."""
        # First convert to sRGB for HSV calculation
        def linear_to_srgb_norm(component: Decimal) -> Decimal:
            if component <= Decimal('0.0031308'):
                return component * Decimal('12.92')
            else:
                return Decimal('1.055') * (component ** (Decimal('1') / Decimal('2.4'))) - Decimal('0.055')

        r_norm = linear_to_srgb_norm(self.red)
        g_norm = linear_to_srgb_norm(self.green)
        b_norm = linear_to_srgb_norm(self.blue)

        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val

        # Value
        value = max_val

        if max_val == 0:
            # Black
            hue = Decimal('0')
            saturation = Decimal('0')
        elif diff == 0:
            # Achromatic (gray)
            hue = Decimal('0')
            saturation = Decimal('0')
        else:
            # Saturation
            saturation = diff / max_val

            # Hue
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


    def with_lightness(self, lightness: Decimal) -> Self:
        """Create new color with different lightness in HSL space."""
        h, s, _ = self.to_hsl()
        return self.__class__.from_hsl(h, s, lightness)

    def with_alpha(self, alpha: Decimal) -> ColorWithAlpha:
        """Add alpha channel."""
        return ColorWithAlpha(self, alpha)

    def luminance(self) -> Decimal:
        """Calculate WCAG relative luminance."""
        from bukzor_color.encodings.wcag_hcl import WcagHCLEncoding

        wcag = WcagHCLEncoding.encode(self)
        return wcag.l

    def contrast_ratio(self, other: 'Color') -> Decimal:
        """Calculate WCAG contrast ratio with another color."""
        l1 = self.luminance()
        l2 = other.luminance()

        # Ensure lighter color is in numerator
        if l1 > l2:
            ratio = (l1 + Decimal('0.05')) / (l2 + Decimal('0.05'))
        else:
            ratio = (l2 + Decimal('0.05')) / (l1 + Decimal('0.05'))

        return ratio

    def encode[T: ColorEncoding](self, encoding_type: type[T]) -> T:
        """Encode this color to the specified encoding format."""
        return encoding_type.encode(self)


@dataclass(frozen=True, slots=True)
class ColorWithAlpha:
    """Color with alpha channel for transparency."""

    color: Color
    alpha: Decimal  # 0-1 range

    def __post_init__(self) -> None:
        """Validate alpha value."""
        if not 0 <= self.alpha <= 1:
            raise ValueError(f"Alpha must be 0-1, got {self.alpha}")

    def over(self, background: Color) -> Color:
        """Composite over background using alpha blending."""
        # Alpha compositing in linear RGB space
        alpha = self.alpha
        inv_alpha = 1 - alpha

        return Color.from_linear_rgb(
            alpha * self.color.red + inv_alpha * background.red,
            alpha * self.color.green + inv_alpha * background.green,
            alpha * self.color.blue + inv_alpha * background.blue
        )