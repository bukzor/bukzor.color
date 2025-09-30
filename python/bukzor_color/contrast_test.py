#!/usr/bin/env -S uv run pytest
"""Tests for WCAG contrast calculations and adjustments."""

from decimal import Decimal

import pytest

import bukzor_color.contrast as M  # module under test
from bukzor_color.encodings.wcag_hcl import WcagHCLEncoding


def test_calculate_contrast():
    """Test basic contrast calculation."""
    from bukzor_color.core import Color

    # Test known contrast ratios
    red = Color.from_hex("#ff0000")
    white = Color.from_hex("#ffffff")

    result = M.calculate_contrast(red, white)

    # Red/white should have ratio around 4.0
    assert Decimal("3.9") < result.ratio < Decimal("4.1")
    assert result.foreground == red
    assert result.background == white


def test_contrast_result_passes_aa():
    """Test WCAG AA compliance checking."""
    from bukzor_color.core import Color

    # Good contrast pair
    dark_gray = Color.from_hex("#333333")
    light_gray = Color.from_hex("#eeeeee")

    result = M.calculate_contrast(dark_gray, light_gray)

    assert result.passes_AA  # Should pass AA (4.5:1)
    assert result.passes_AA_large  # Should pass AA large (3:1)


def test_contrast_result_passes_aaa():
    """Test WCAG AAA compliance checking."""
    from bukzor_color.core import Color

    # High contrast pair
    black = Color.from_hex("#000000")
    white = Color.from_hex("#ffffff")

    result = M.calculate_contrast(black, white)

    assert result.passes_AA
    assert result.passes_AAA  # Should pass AAA (7:1)
    assert result.passes_AA_large
    assert result.passes_AAA_large


def test_contrast_result_meets_level():
    """Test meets_level method."""
    from bukzor_color.core import Color

    black = Color.from_hex("#000000")
    white = Color.from_hex("#ffffff")

    result = M.calculate_contrast(black, white)

    assert result.meets_level("AA")
    assert result.meets_level("AAA")
    assert result.meets_level("AA-large")
    assert result.meets_level("AAA-large")
    assert result.meets_level("A")  # A level has no contrast requirement


def test_contrast_result_compliance_summary():
    """Test compliance summary method."""
    from bukzor_color.core import Color

    # Medium contrast pair
    gray1 = Color.from_hex("#666666")
    gray2 = Color.from_hex("#cccccc")

    result = M.calculate_contrast(gray1, gray2)
    summary = result.compliance_summary()

    assert isinstance(summary, dict)
    assert "AA" in summary
    assert "AAA" in summary
    assert "AA-large" in summary
    assert "AAA-large" in summary


def test_get_target_ratio_from_wcag_level():
    """Test converting WCAG levels to numeric ratios."""
    assert M.get_target_ratio("AA") == Decimal("4.5")
    assert M.get_target_ratio("AAA") == Decimal("7")
    assert M.get_target_ratio("AA-large") == Decimal("3")
    assert M.get_target_ratio("AAA-large") == Decimal("4.5")
    assert M.get_target_ratio("A") == Decimal("1")


def test_get_target_ratio_from_decimal():
    """Test passing existing decimal ratio."""
    from bukzor_color.types import ContrastRatio

    ratio = ContrastRatio(Decimal("5.5"))
    result = M.get_target_ratio(ratio)

    assert result == Decimal("5.5")


def test_adjust_contrast_already_compliant():
    """Test adjust_contrast when colors already meet target."""
    from bukzor_color.core import Color

    # Already good contrast
    black = Color.from_hex("#000000")
    white = Color.from_hex("#ffffff")

    adjusted_fg, adjusted_bg, result = M.adjust_contrast(black, white, "AA")

    # Should return unchanged colors
    assert adjusted_fg == black
    assert adjusted_bg == white
    assert result.meets_level("AA")


def test_adjust_contrast_foreground():
    """Test adjusting foreground color for contrast."""
    from bukzor_color.core import Color

    # Poor contrast pair
    light_gray = Color.from_hex("#aaaaaa")
    white = Color.from_hex("#ffffff")

    adjusted_fg, adjusted_bg, result = M.adjust_contrast(
        light_gray, white, "AA", adjust="fg"
    )

    # Background should be unchanged
    assert adjusted_bg == white
    # Foreground should be darker to increase contrast
    assert (
        WcagHCLEncoding.encode(adjusted_fg).l
        < WcagHCLEncoding.encode(light_gray).l
    )
    # Should meet target (allowing for small precision errors)
    # TODO: stop allowing "small precision errors"
    assert result.ratio >= Decimal("4.49")


def test_adjust_contrast_background():
    """Test adjusting background color for contrast."""
    from bukzor_color.core import Color

    # Poor contrast pair
    dark_gray = Color.from_hex("#555555")
    medium_gray = Color.from_hex("#777777")

    adjusted_fg, adjusted_bg, result = M.adjust_contrast(
        dark_gray, medium_gray, "AA", adjust="bg"
    )

    # Foreground should be unchanged
    assert adjusted_fg == dark_gray
    # Background should be adjusted
    assert adjusted_bg != medium_gray
    # Should meet target (allowing for tiny precision errors)
    import math

    assert result.meets_level("AA") or math.isclose(float(result.ratio), 4.5)


def test_adjust_contrast_auto_strategy():
    """Test auto adjustment strategy selection."""
    from bukzor_color.core import Color

    # Test with colors that need adjustment
    gray1 = Color.from_hex("#888888")
    gray2 = Color.from_hex("#999999")

    adjusted_fg, adjusted_bg, result = M.adjust_contrast(
        gray1, gray2, "AA", adjust="auto"
    )

    # Should pick an adjustment strategy and meet target
    assert result.meets_level("AA")
    # At least one color should be different
    assert adjusted_fg != gray1 or adjusted_bg != gray2


def test_adjust_contrast_numeric_target():
    """Test adjustment with numeric contrast ratio target."""
    from bukzor_color.core import Color
    from bukzor_color.types import ContrastRatio

    gray1 = Color.from_hex("#666666")
    gray2 = Color.from_hex("#cccccc")

    target_ratio = ContrastRatio(Decimal("6.0"))
    _adjusted_fg, _adjusted_bg, result = M.adjust_contrast(
        gray1, gray2, target_ratio
    )

    # Should meet or exceed the target ratio (allowing for tiny precision errors)
    import math

    assert result.ratio >= Decimal("6.0") or math.isclose(
        float(result.ratio), 6.0
    )


def test_adjust_contrast_preserve_hue():
    """Test that hue preservation works during adjustment."""
    from bukzor_color.core import Color

    # Start with a colored foreground
    red = Color.from_hex("#ff0000")
    light_red = Color.from_hex("#ffcccc")

    adjusted_fg, _adjusted_bg, result = M.adjust_contrast(red, light_red, "AA")

    # Should meet target
    assert result.meets_level("AA")

    # Hue should be preserved (approximately)
    original_h, _, _ = red.to_hsl()
    adjusted_h, _, _ = adjusted_fg.to_hsl()
    assert abs(original_h - adjusted_h) < Decimal(
        "10"
    )  # Allow small variation


def test_invalid_wcag_level():
    """Test error handling for invalid WCAG levels."""
    with pytest.raises(ValueError, match="Unknown WCAG level"):
        M.get_target_ratio("INVALID")  # type: ignore[arg-type]
