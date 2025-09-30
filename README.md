# bukzor.color

Color calculations and conversions CLI utility with implementations in both Rust
and Python.

## Features

- Color format conversions (hex, RGB, HSL, HSV)
- JSON output for jq compatibility
- Bash-friendly CLI interface
- Dual implementations for performance and portability

## Implementations

This repository contains two implementations of the same CLI tool:

- **Rust** (`./rust/`): High-performance native binary
- **Python** (`./python/`): Cross-platform with rich ecosystem

Both implementations provide identical CLI interfaces and JSON output formats.

## Quick Start

### Rust Implementation

```bash
cd rust
cargo build --release
./target/release/bukzor-color convert "#ff0000" --to rgb --json
```

### Python Implementation

```bash
cd python
uv sync
uv run bukzor-color convert "#ff0000" --to rgb --json
```

## Usage

```bash
# Convert colors between formats
bukzor-color convert "#ff0000" --to rgb
bukzor-color convert "rgb(255,0,0)" --to hsl

# JSON output for scripting
bukzor-color convert "#ff0000" --to rgb --json | jq .result

# Get help
bukzor-color --help
bukzor-color convert --help
```

## Development

### Prerequisites

- **Rust**: `rustc`, `cargo`
- **Python**: Python 3.13+, `uv`
- **Node.js**: For prettier/formatting (pnpm)

### Setup

```bash
# Install development dependencies
pnpm install
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Testing

```bash
# Run acceptance tests for both implementations
./tests/acceptance-test

# Format and lint all code
uv run pre-commit run --all-files
```

### Project Structure

```
bukzor.color/
├── rust/              # Rust implementation
├── python/            # Python implementation
├── tests/             # Cross-implementation acceptance tests
├── .github/workflows/ # CI/CD pipelines
└── README.md          # This file
```

## Repository Conventions

This repository follows established patterns for multi-language implementations:

- **Single repository**: Keeps implementations in sync
- **Language subdirectories**: `rust/`, `python/`
- **Shared tooling**: Pre-commit, prettier, CI/CD
- **Cross-language tests**: Ensures consistency between implementations

## License

Apache-2.0
