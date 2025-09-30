"""Type definitions for bukzor.color library."""

from decimal import Decimal
from typing import NewType, Literal

# Specific numeric types for color components
Byte = NewType('Byte', int)  # 0-255
Percentage = NewType('Percentage', Decimal)  # 0.0-100.0
Degrees = NewType('Degrees', Decimal)  # 0.0-360.0
Ratio = NewType('Ratio', Decimal)  # 0.0-1.0

# Color channel types
RGBChannel = Byte
HSLHue = Degrees
HSLSaturation = Percentage
HSLLightness = Percentage
HSVHue = Degrees
HSVSaturation = Percentage
HSVValue = Percentage

# Contrast types
ContrastRatio = NewType('ContrastRatio', Decimal)  # 1.0-21.0
Luminance = NewType('Luminance', Decimal)  # 0.0-1.0

# WCAG compliance levels
WCAGLevel = Literal["A", "AA", "AAA", "AA-large", "AAA-large"]

# Adjustment targets
AdjustTarget = Literal["fg", "bg", "both", "auto"]

# Terminal color types
ANSIIndex = NewType('ANSIIndex', int)  # 0-255
TerminalPalette = Literal["ansi16", "ansi256", "rgb"]

# Color space identifiers
ColorSpace = Literal["rgb", "hsl", "hsv", "lab", "lch", "oklab", "oklch", "xyz"]

# Distance calculation methods
DistanceMethod = Literal["euclidean", "perceptual", "cie76", "cie94", "cie2000"]

# Color scheme types
SchemeType = Literal["monochrome", "analogous", "complementary", "triadic", "tetradic", "split-complementary"]