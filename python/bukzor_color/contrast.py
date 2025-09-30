"""WCAG contrast calculations and accessibility functions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from bukzor_color.core import Color
from bukzor_color.encodings.wcag_hcl import WcagHCLEncoding
from bukzor_color.types import AdjustTarget
from bukzor_color.types import ContrastRatio
from bukzor_color.types import Degrees
from bukzor_color.types import Luminance
from bukzor_color.types import Percentage
from bukzor_color.types import WCAGLevel


@dataclass(frozen=True, slots=True)
class ContrastResult:
    """Result of contrast calculation between two colors."""

    foreground: Color
    background: Color
    ratio: ContrastRatio

    @property
    def passes_AA(self) -> bool:
        """Check if contrast meets WCAG AA standard (4.5:1)."""
        return self.ratio >= Decimal("4.5")

    @property
    def passes_AAA(self) -> bool:
        """Check if contrast meets WCAG AAA standard (7:1)."""
        return self.ratio >= Decimal("7")

    @property
    def passes_AA_large(self) -> bool:
        """Check if contrast meets WCAG AA large text standard (3:1)."""
        return self.ratio >= Decimal("3")

    @property
    def passes_AAA_large(self) -> bool:
        """Check if contrast meets WCAG AAA large text standard (4.5:1)."""
        return self.ratio >= Decimal("4.5")

    def meets_level(self, level: WCAGLevel) -> bool:
        """Check if contrast meets specified WCAG level."""
        if level == "AA":
            return self.passes_AA
        elif level == "AAA":
            return self.passes_AAA
        elif level == "AA-large":
            return self.passes_AA_large
        elif level == "AAA-large":
            return self.passes_AAA_large
        elif level == "A":
            # WCAG A doesn't specify contrast requirements
            return True
        else:
            raise ValueError(f"Unknown WCAG level: {level}")

    def compliance_summary(self) -> dict[str, bool]:
        """Get summary of all compliance levels."""
        return {
            "AA": self.passes_AA,
            "AAA": self.passes_AAA,
            "AA-large": self.passes_AA_large,
            "AAA-large": self.passes_AAA_large,
        }


def calculate_contrast(fg: Color, bg: Color) -> ContrastResult:
    """Calculate WCAG contrast ratio between two colors."""
    fg_wcag = WcagHCLEncoding.encode(fg)
    bg_wcag = WcagHCLEncoding.encode(bg)

    l1 = fg_wcag.l
    l2 = bg_wcag.l

    # Ensure lighter color is in numerator
    if l1 > l2:
        ratio = ContrastRatio((l1 + Decimal("0.05")) / (l2 + Decimal("0.05")))
    else:
        ratio = ContrastRatio((l2 + Decimal("0.05")) / (l1 + Decimal("0.05")))

    return ContrastResult(foreground=fg, background=bg, ratio=ratio)


def get_target_ratio(level: WCAGLevel | ContrastRatio) -> ContrastRatio:
    """Convert WCAG level to numeric contrast ratio."""
    # Check if it's already a Decimal (ContrastRatio is NewType of Decimal)
    if isinstance(level, Decimal):
        return ContrastRatio(level)

    ratio_map = {
        "A": Decimal("1"),  # No specific requirement
        "AA": Decimal("4.5"),
        "AAA": Decimal("7"),
        "AA-large": Decimal("3"),
        "AAA-large": Decimal("4.5"),
    }

    if level in ratio_map:
        return ContrastRatio(ratio_map[level])
    else:
        raise ValueError(f"Unknown WCAG level: {level}")


def adjust_contrast(
    fg: Color,
    bg: Color,
    target: ContrastRatio | WCAGLevel,
    adjust: AdjustTarget = "fg",
) -> tuple[Color, Color, ContrastResult]:
    """
    Adjust colors to meet target contrast ratio.

    Args:
        fg: Foreground color
        bg: Background color
        target: Target contrast ratio or WCAG level
        adjust: Which color to adjust ("fg", "bg")

    Returns:
        Tuple of (adjusted_fg, adjusted_bg, contrast_result)
    """
    target_ratio = get_target_ratio(target)
    current_result = calculate_contrast(fg, bg)

    # If already meets target, return unchanged
    if current_result.ratio >= target_ratio:
        return fg, bg, current_result

    if adjust == "fg":
        adjusted_fg = _adjust_lightness_for_contrast(fg, bg, target_ratio)
        result = calculate_contrast(adjusted_fg, bg)
        return adjusted_fg, bg, result
    elif adjust == "bg":
        adjusted_bg = _adjust_lightness_for_contrast(bg, fg, target_ratio)
        result = calculate_contrast(fg, adjusted_bg)
        return fg, adjusted_bg, result
    elif adjust == "auto":
        # Try both approaches and choose the one that requires less change
        try:
            adjusted_fg = _adjust_lightness_for_contrast(fg, bg, target_ratio)
            fg_result = calculate_contrast(adjusted_fg, bg)
            fg_change = abs(fg.luminance() - adjusted_fg.luminance())
        except Exception:
            fg_change = Decimal("inf")
            fg_result = current_result
            adjusted_fg = fg

        try:
            adjusted_bg = _adjust_lightness_for_contrast(bg, fg, target_ratio)
            bg_result = calculate_contrast(fg, adjusted_bg)
            bg_change = abs(bg.luminance() - adjusted_bg.luminance())
        except Exception:
            bg_change = Decimal("inf")
            bg_result = current_result
            adjusted_bg = bg

        # Choose the strategy with minimal change that meets target
        if fg_result.ratio >= target_ratio and bg_result.ratio >= target_ratio:
            if fg_change <= bg_change:
                return adjusted_fg, bg, fg_result
            else:
                return fg, adjusted_bg, bg_result
        elif fg_result.ratio >= target_ratio:
            return adjusted_fg, bg, fg_result
        elif bg_result.ratio >= target_ratio:
            return fg, adjusted_bg, bg_result
        else:
            # Neither meets target, choose the better one
            if fg_result.ratio >= bg_result.ratio:
                return adjusted_fg, bg, fg_result
            else:
                return fg, adjusted_bg, bg_result
    else:
        raise ValueError(
            f"Invalid adjust target: {adjust}. Must be 'fg', 'bg', or 'auto'"
        )


def _adjust_lightness_for_contrast(
    color_to_adjust: Color, fixed_color: Color, target_ratio: ContrastRatio
) -> Color:
    """Adjust lightness of one color to achieve target contrast with another."""
    # Convert to WCAG HCL for direct luminance control
    adjust_wcag = WcagHCLEncoding.encode(color_to_adjust)
    fixed_wcag = WcagHCLEncoding.encode(fixed_color)

    h, c = adjust_wcag.h, adjust_wcag.c

    # Solve: target_ratio = (L_adjust + 0.05) / (L_fixed + 0.05)
    # So: L_adjust = target_ratio * (L_fixed + 0.05) - 0.05
    required_luminance_1 = target_ratio * (
        fixed_wcag.l + Decimal("0.05")
    ) - Decimal("0.05")

    # Also try the inverse case: target_ratio = (L_fixed + 0.05) / (L_adjust + 0.05)
    # So: L_adjust = (L_fixed + 0.05) / target_ratio - 0.05
    required_luminance_2 = (
        fixed_wcag.l + Decimal("0.05")
    ) / target_ratio - Decimal("0.05")

    # Try both luminance options and pick the valid one closest to current
    candidates: list[tuple[Color, ContrastRatio, Decimal]] = []
    for req_lum in [required_luminance_1, required_luminance_2]:
        # Create test color with new luminance
        test_color = WcagHCLEncoding(
            Degrees(h), Percentage(c), Luminance(req_lum)
        ).decode()
        test_ratio = calculate_contrast(test_color, fixed_color).ratio
        candidates.append((test_color, test_ratio, req_lum))

    # Find the best candidate that meets the target
    best_candidate: tuple[Color, ContrastRatio, Decimal] | None = None
    for color, ratio, luminance in candidates:
        if ratio >= target_ratio:
            if best_candidate is None or ratio < best_candidate[1]:
                best_candidate = (color, ratio, luminance)

    if best_candidate:
        return best_candidate[0]
    else:
        # Return the candidate closest to target
        if candidates:
            candidates.sort(key=lambda x: abs(x[1] - target_ratio))
            return candidates[0][0]
        else:
            return color_to_adjust
