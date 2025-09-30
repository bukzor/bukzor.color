#!/usr/bin/env -S uv run pytest
"""Tests for core Color functionality."""

from decimal import Decimal

import pytest

import bukzor_color.core as M  # module under test


def test_color_from_hex():
    """Test creating Color from hex string."""
    color = M.Color.from_hex("#ff0000")
    r, g, b = color.to_srgb()
    assert r == 255
    assert g == 0
    assert b == 0


def test_color_from_srgb():
    """Test creating Color from sRGB values."""
    color = M.Color.from_srgb(255, 0, 0)
    assert color.to_hex() == "#ff0000"


def test_color_from_hsl():
    """Test creating Color from HSL values."""
    # Pure red: H=0, S=100%, L=50%
    color = M.Color.from_hsl(Decimal('0'), Decimal('100'), Decimal('50'))
    r, g, b = color.to_srgb()
    assert r == 255
    assert g == 0
    assert b == 0


def test_color_to_hsl():
    """Test converting Color to HSL."""
    color = M.Color.from_hex("#ff0000")
    h, s, l = color.to_hsl()
    assert h == Decimal('0')
    assert s == Decimal('100')
    assert l == Decimal('50')


def test_luminance_calculation():
    """Test WCAG luminance calculation."""
    # Test known values
    white = M.Color.from_hex("#ffffff")
    black = M.Color.from_hex("#000000")
    red = M.Color.from_hex("#ff0000")

    white_lum = white.luminance()
    black_lum = black.luminance()
    red_lum = red.luminance()

    # White should have highest luminance
    assert white_lum > red_lum > black_lum
    # Black should be very close to 0
    assert black_lum < Decimal('0.01')


def test_contrast_ratio():
    """Test contrast ratio calculation between colors."""
    red = M.Color.from_hex("#ff0000")
    white = M.Color.from_hex("#ffffff")

    ratio = red.contrast_ratio(white)
    # Red/white should have ratio around 4.0
    assert Decimal('3.9') < ratio < Decimal('4.1')


def test_with_lightness():
    """Test creating color with different lightness."""
    red = M.Color.from_hex("#ff0000")
    darker_red = red.with_lightness(Decimal('25'))

    h1, s1, _ = red.to_hsl()
    h2, s2, l2 = darker_red.to_hsl()

    # Hue and saturation should be preserved
    assert h1 == h2
    assert s1 == s2
    # Lightness should be changed
    assert l2 == Decimal('25')


def test_with_alpha():
    """Test adding alpha channel to color."""
    red = M.Color.from_hex("#ff0000")
    red_alpha = red.with_alpha(Decimal('0.5'))

    assert isinstance(red_alpha, M.ColorWithAlpha)
    assert red_alpha.alpha == Decimal('0.5')
    assert red_alpha.color == red


def test_color_validation():
    """Test color component validation."""
    with pytest.raises(ValueError, match="Color red must be 0-1"):
        M.Color.from_linear_rgb(Decimal('2'), Decimal('0'), Decimal('0'))

    with pytest.raises(ValueError, match="Color green must be 0-1"):
        M.Color.from_linear_rgb(Decimal('0'), Decimal('-1'), Decimal('0'))


def test_alpha_compositing():
    """Test alpha compositing over background."""
    red = M.Color.from_hex("#ff0000")
    white = M.Color.from_hex("#ffffff")

    # 50% red over white should give pink
    red_alpha = red.with_alpha(Decimal('0.5'))
    result = red_alpha.over(white)

    # Result should be exactly calculable
    result_rgb = result.to_srgb()
    # With 50% alpha: 0.5 * red + 0.5 * white in linear space, then converted to sRGB
    assert result_rgb == (255, 188, 188)