# Bash Scripting Patterns

## Script Headers

Always start scripts with proper error handling:

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
exec 2>&1          # Prevent stderr de-interleaving (especially in CI)
```

## Debugging Support

For scripts that need debugging visibility:

```bash
# After constants/configuration
PS4=$'\n${TEAL}${NC} '  # Or appropriate colors
set -x                   # Enable trace mode
```

## Status Messages

```bash
: "Status message"       # ✓ Use colon operator for traced scripts
echo "Status message"    # ✗ Avoid in scripts with set -x (double output)
```

The `:` (colon) command is a no-op that evaluates its arguments, making it perfect for status messages in traced scripts.

## Directory Changes

### ✓ Good: Subshells preserve working directory
```bash
(cd subdir && command)         # Returns to original dir
(cd rust && cargo build)       # Directory change is isolated
```

### ✗ Bad: Global directory changes
```bash
cd subdir && command           # Permanently changes directory
cd rust                        # Affects all subsequent commands
cargo build
```

### Alternative: Avoid cd entirely
```bash
cargo --manifest-path rust/Cargo.toml build
command --working-dir subdir
```

## Error Handling

Never suppress errors in tests or CI:

```bash
# ✗ Bad - hides failures
if command >/dev/null 2>&1; then

# ✓ Good - failures are visible
if command; then
```

## Command Chaining

```bash
# Simple sequential execution
cmd1 && cmd2 && cmd3

# With error handling
if ! cmd1; then
    : "Error message"
    exit 1
fi
```

## Color Variables

Define at script start:
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
TEAL='\033[0;36m'
NC='\033[0m'  # No Color
```

## Arithmetic

```bash
((var++))                    # Increment
((failures += 1))            # Add to counter
total=$((val1 + val2))       # Calculate total
```

## Testing Commands

```bash
# Check if command exists
if command -v cargo; then
    # cargo is available
fi

# Note: No >/dev/null needed with command -v
```