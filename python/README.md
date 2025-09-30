# bukzor-color (Python Implementation)

Python implementation of the bukzor.color CLI utility for color calculations and
conversions.

## Installation

```bash
# Install in development mode
uv sync
uv pip install -e .

# Or install from PyPI (when published)
pip install bukzor-color
```

## Usage

```bash
# Convert a color to hex format (default)
bukzor-color convert "#ff0000"

# Convert to specific format
bukzor-color convert "#ff0000" --to rgb

# JSON output for jq compatibility
bukzor-color convert "#ff0000" --to hsl --json
```

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run pyright
```
