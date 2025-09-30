# bukzor-color (Rust Implementation)

Rust implementation of the bukzor.color CLI utility for color calculations and
conversions.

## Building

```bash
cargo build --release
```

## Usage

```bash
# Convert a color to hex format (default)
cargo run -- convert "#ff0000"

# Convert to specific format
cargo run -- convert "#ff0000" --to rgb

# JSON output for jq compatibility
cargo run -- convert "#ff0000" --to hsl --json
```

## Installation

```bash
cargo install --path .
```
