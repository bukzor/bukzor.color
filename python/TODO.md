# TODO

## Remaining Tasks

1. **Remove Color.luminance() method**
   - Still called in: contrast.py (one place), core.py, encodings_test.py,
     contrast_test.py, core_test.py, models.py
   - Replace all calls with `wcag_luminance()` function or WCAG HCL encoding
   - Remove the method from core.py after all usages are gone

2. **Convert HSLEncoding to store values as [0-1) numbers instead of
   percentages**
   - Currently stores S and L as 0-100 percentages
   - Should store as 0-1 decimal values for consistency

3. **Fix remaining .luminance() calls in other modules**
   - contrast.py: Still has calls in `_determine_optimal_adjustment` function
   - models.py: Uses .luminance() for contrast calculations
   - Update all to use WCAG HCL encoding consistently

4. **Clean up WCAG HCL**
   - Consider making `wcag_luminance()` function more prominent in public API
   - Ensure all WCAG-related code uses the same luminance source

5. **Stop allowing "small precision errors"**
   - Currently tests use `assert result.ratio >= Decimal('4.49')` instead of
     proper 4.5
   - Fix precision issues in contrast calculations to meet exact WCAG
     requirements
   - Remove workarounds and ensure calculations are mathematically precise

## Completed ✓

- ✅ Fixed WCAG HCL to use exact WCAG luminance as L (not HSL lightness)
- ✅ Implemented working WCAG HCL with orthogonal basis projection
- ✅ Made WCAG HCL self-contained with its own coefficients
- ✅ Partially fixed contrast.py to use WCAG encoding instead of
  Color.luminance()
