#!/usr/bin/env -S uv run pytest
"""Tests for color encoding/decoding functionality."""

from decimal import Decimal

import pytest
from hypothesis import given, strategies as st, example

from bukzor_color.encodings import encodings as M  # module under test
from bukzor_color.types import Degrees, Percentage, Luminance


def test_hex_encoding_parse_6_char():
    """Test parsing 6-character hex codes."""
    encoding = M.HexEncoding.parse("#ff0000")
    assert str(encoding) == "#ff0000"

    color = encoding.decode()
    r, g, b = color.to_srgb()
    assert r == 255
    assert g == 0
    assert b == 0


def test_hex_encoding_parse_3_char():
    """Test parsing 3-character hex codes (expansion)."""
    encoding = M.HexEncoding.parse("#f00")
    assert str(encoding) == "#ff0000"  # Should expand

    color = encoding.decode()
    r, g, b = color.to_srgb()
    assert r == 255
    assert g == 0
    assert b == 0


def test_hex_encoding_parse_without_hash():
    """Test parsing hex without # prefix."""
    encoding = M.HexEncoding.parse("ff0000")
    assert str(encoding) == "#ff0000"


def test_hex_encoding_encode():
    """Test encoding Color to hex."""
    from bukzor_color.core import Color

    color = Color.from_srgb(255, 0, 0)
    encoding = color.encode(M.HexEncoding)
    assert str(encoding) == "#ff0000"


def test_rgb_encoding_parse():
    """Test parsing RGB string."""
    encoding = M.RGBEncoding.parse("rgb(255, 0, 0)")
    assert encoding.r == 255
    assert encoding.g == 0
    assert encoding.b == 0

    color = encoding.decode()
    assert color.to_hex() == "#ff0000"


def test_rgb_encoding_encode():
    """Test encoding Color to RGB."""
    from bukzor_color.core import Color

    color = Color.from_hex("#ff0000")
    encoding = color.encode(M.RGBEncoding)
    assert encoding.r == 255
    assert encoding.g == 0
    assert encoding.b == 0
    assert str(encoding) == "rgb(255, 0, 0)"


def test_hsl_encoding_parse():
    """Test parsing HSL string."""
    encoding = M.HSLEncoding.parse("hsl(0, 100%, 50%)")
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.l == Decimal('50')

    color = encoding.decode()
    assert color.to_hex() == "#ff0000"


def test_hsl_encoding_encode():
    """Test encoding Color to HSL."""
    from bukzor_color.core import Color

    color = Color.from_hex("#ff0000")
    encoding = color.encode(M.HSLEncoding)
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.l == Decimal('50')
    assert str(encoding) == "hsl(0, 100%, 50%)"


def test_hsv_encoding_parse():
    """Test parsing HSV string."""
    encoding = M.HSVEncoding.parse("hsv(0, 100%, 100%)")
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.v == Decimal('100')

    color = encoding.decode()
    # HSV(0, 100%, 100%) should be pure red
    r, g, b = color.to_srgb()
    assert r == 255
    assert g == 0
    assert b == 0


def test_hsv_encoding_encode():
    """Test encoding Color to HSV."""
    from bukzor_color.core import Color

    color = Color.from_hex("#ff0000")
    encoding = color.encode(M.HSVEncoding)
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.v == Decimal('100')
    assert str(encoding) == "hsv(0, 100%, 100%)"


def test_auto_parse_hex():
    """Test auto-parsing hex colors."""
    # 6-character hex
    encoding = M.auto_parse("#ff0000")
    assert isinstance(encoding, M.HexEncoding)
    assert str(encoding) == "#ff0000"

    # 3-character hex
    encoding = M.auto_parse("#f00")
    assert isinstance(encoding, M.HexEncoding)
    assert str(encoding) == "#ff0000"


def test_auto_parse_rgb():
    """Test auto-parsing RGB colors."""
    encoding = M.auto_parse("rgb(255, 0, 0)")
    assert isinstance(encoding, M.RGBEncoding)
    assert encoding.r == 255
    assert encoding.g == 0
    assert encoding.b == 0


def test_auto_parse_hsl():
    """Test auto-parsing HSL colors."""
    encoding = M.auto_parse("hsl(0, 100%, 50%)")
    assert isinstance(encoding, M.HSLEncoding)
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.l == Decimal('50')


def test_auto_parse_hsv():
    """Test auto-parsing HSV colors."""
    encoding = M.auto_parse("hsv(0, 100%, 100%)")
    assert isinstance(encoding, M.HSVEncoding)
    assert encoding.h == Decimal('0')
    assert encoding.s == Decimal('100')
    assert encoding.v == Decimal('100')


def test_auto_parse_css_named_color():
    """Test auto-parsing CSS named colors."""
    encoding = M.auto_parse("red")
    assert isinstance(encoding, M.HexEncoding)
    assert str(encoding) == "#ff0000"

    encoding = M.auto_parse("white")
    assert isinstance(encoding, M.HexEncoding)
    assert str(encoding) == "#ffffff"


def test_invalid_formats():
    """Test error handling for invalid formats."""
    with pytest.raises(ValueError, match="Invalid hex format"):
        M.HexEncoding.parse("#gggggg")

    with pytest.raises(ValueError, match="Invalid RGB format"):
        M.RGBEncoding.parse("rgb(256, 0, 0, extra)")

    with pytest.raises(ValueError, match="Invalid HSL format"):
        M.HSLEncoding.parse("hsl(0, 100)")

    with pytest.raises(ValueError, match="Cannot auto-detect color format"):
        M.auto_parse("not-a-color")


@given(
    hue=st.decimals(min_value=-720, max_value=720, places=2),
    luminance=st.decimals(min_value=0, max_value=1, places=3)
)
@example(hue=Decimal('0'), luminance=Decimal('1.0'))  # Should be white
@example(hue=Decimal('0'), luminance=Decimal('0.0'))  # Should be black
@example(hue=Decimal('120'), luminance=Decimal('1.0'))  # Should be white regardless of hue
@example(hue=Decimal('240'), luminance=Decimal('0.5'))  # Should be gray regardless of hue
def test_wcag_hcl_achromatic_preserves_luminance(hue: Decimal, luminance: Decimal):
    """Test that WCAG HCL with zero chroma preserves luminance regardless of hue."""
    from bukzor_color.encodings.wcag_hcl import WcagHCLEncoding

    color = WcagHCLEncoding(Degrees(hue), Percentage(Decimal('0')), Luminance(luminance)).decode()

    # Should preserve the exact luminance
    actual_luminance = color.luminance()
    assert abs(actual_luminance - luminance) < Decimal('0.001'), \
        f"h={hue}, c=0, l={luminance} -> actual luminance {actual_luminance}"

    # Should be achromatic (gray/white/black)
    r, g, b = color.red, color.green, color.blue
    assert abs(r - g) < Decimal('0.001'), f"Should be achromatic: R={r}, G={g}, B={b}"
    assert abs(g - b) < Decimal('0.001'), f"Should be achromatic: R={r}, G={g}, B={b}"


@given(
    r=st.decimals(min_value=0, max_value=1, places=3),
    g=st.decimals(min_value=0, max_value=1, places=3),
    b=st.decimals(min_value=0, max_value=1, places=3)
)
def test_wcag_hcl_round_trip(r: Decimal, g: Decimal, b: Decimal):
    """Test that WCAG HCL encoding/decoding preserves colors."""
    from bukzor_color.core import Color
    from bukzor_color.encodings.wcag_hcl import WcagHCLEncoding

    # Start with RGB color
    original_color = Color.from_linear_rgb(r, g, b)

    # Encode to WCAG HCL
    wcag_hcl = WcagHCLEncoding.encode(original_color)

    # Decode back to RGB
    reconstructed_color = wcag_hcl.decode()

    # Should preserve the original color
    assert abs(reconstructed_color.red - r) < Decimal('0.001'), \
        f"Red: {r} -> {reconstructed_color.red}"
    assert abs(reconstructed_color.green - g) < Decimal('0.001'), \
        f"Green: {g} -> {reconstructed_color.green}"
    assert abs(reconstructed_color.blue - b) < Decimal('0.001'), \
        f"Blue: {b} -> {reconstructed_color.blue}"


def test_round_trip_conversions():
    """Test round-trip encoding/decoding preserves colors."""
    original_hex = "#ff0000"

    # Hex -> Color -> Hex
    hex_encoding = M.HexEncoding.parse(original_hex)
    color = hex_encoding.decode()
    new_hex_encoding = color.encode(M.HexEncoding)
    assert str(new_hex_encoding) == original_hex

    # RGB -> Color -> RGB
    from bukzor_color.core import Color
    rgb_color = Color.from_srgb(255, 0, 0)
    rgb_encoding = rgb_color.encode(M.RGBEncoding)
    color = rgb_encoding.decode()
    new_rgb_encoding = color.encode(M.RGBEncoding)
    assert new_rgb_encoding.r == 255
    assert new_rgb_encoding.g == 0
    assert new_rgb_encoding.b == 0

    # HSL -> Color -> HSL (approximately, due to rounding)
    hsl_color = Color.from_hsl(Decimal('0'), Decimal('100'), Decimal('50'))
    hsl_encoding = hsl_color.encode(M.HSLEncoding)
    color = hsl_encoding.decode()
    new_hsl_encoding = color.encode(M.HSLEncoding)
    assert abs(new_hsl_encoding.h - Decimal('0')) < Decimal('1')
    assert abs(new_hsl_encoding.s - Decimal('100')) < Decimal('1')
    assert abs(new_hsl_encoding.l - Decimal('50')) < Decimal('1')