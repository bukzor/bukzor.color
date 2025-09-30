# CLAUDE.md - bukzor.color Project Guide

## Quick Start

This is a **multi-language CLI project** implementing color calculations and conversions in both Rust and Python.

See `.claude/` directory for general development conventions.

## Project Structure

```
bukzor.color/
├── rust/               # Rust implementation
│   ├── Cargo.toml
│   └── src/main.rs
├── python/            # Python implementation
│   ├── pyproject.toml
│   └── bukzor_color/
├── tests/             # Cross-language acceptance tests
│   ├── acceptance-test
│   └── test_cases.json
├── .github/workflows/ # CI pipelines
├── Cargo.toml        # Rust workspace definition
└── pyproject.toml    # Top-level Python dev dependencies
```

## Key Conventions

### Multi-Language Coordination
- Both implementations must pass identical acceptance tests
- Keep CLI interfaces synchronized
- JSON output format must match exactly

### Dependency Management
```bash
# Rust - from workspace root
(cd rust && cargo add <pkg> --features <feat>)

# Python - from project root
uv add <pkg>
```

### Testing
```bash
# Run acceptance tests (tests both implementations)
./tests/acceptance-test

# Run pre-commit checks
uv run pre-commit run --all-files
```

### Git Workflow
- Use regular merge commits (NOT squash): `gh pr merge --merge`
- Amend related fixes: `git commit --amend --no-edit`

## CI/CD Setup

### GitHub Actions
- **pre-commit.yml**: Runs formatters and linters, auto-commits fixes
- **test.yml**: Runs acceptance tests for both implementations
- Uses `HatsuneMiku3939/direnv-action@v1.1.0` for environment setup

### Tool Requirements
- `rust-toolchain.toml`: Specifies Rust 1.90.0
- Python: Requires 3.13+
- Node.js: For prettier and pyright

## Development Environment

### Required Tools
```bash
# Check these are available
cargo --version
uv --version
pnpm --version
direnv --version
```

### Environment Setup
- `.envrc` adds `bin/` to PATH for `pnpm-run` wrapper
- `direnv allow` to activate

## Common Tasks

### Adding a New Color Conversion
1. Implement in `rust/src/main.rs`
2. Implement in `python/bukzor_color/cli.py`
3. Add test case to `tests/test_cases.json`
4. Run `./tests/acceptance-test` to verify

### Updating Dependencies
```bash
# Rust
(cd rust && cargo update)

# Python
uv sync

# Node.js
pnpm update
```

### Pre-commit Hooks
Configured to run:
- prettier (all text files)
- Python: pyupgrade → isort → black → pyright
- Rust: rustfmt → clippy
- Standard checks (trailing whitespace, EOF, etc.)

## Troubleshooting

### CI Failures
- Check `pnpm-run` is available (via direnv)
- Verify Rust version matches rust-toolchain.toml
- Ensure all files end with newline

### Local Development
- If `cargo` commands fail, check rust-toolchain.toml
- For `pnpm-run not found`, run `direnv allow`
- Python issues: ensure `uv sync` has been run

## References
- Original PR: #1 (Initial skeleton)
- General conventions: `.claude/`
- Project repository: https://github.com/bukzor/bukzor.color