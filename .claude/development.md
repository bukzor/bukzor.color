# Development Practices

## Dependency Management

### Let Package Managers Handle Versions

**✓ Good: Use official add commands**
```bash
# Rust
(cd rust && cargo add <package> --features <features>)

# Python
uv add <package>
pip install <package>

# Node.js
pnpm add <package>
npm install <package>
```

**✗ Bad: Manual version editing**
- Don't edit Cargo.toml dependencies manually
- Don't edit package.json dependencies manually
- Let the tools resolve compatible versions

### When to Pin Versions
- Only pin when you need a specific version for compatibility
- Document why with a comment
- Use `cargo update` or `npm update` to manage updates

## Testing Philosophy

### Fail Loudly
```bash
# ✗ Bad - suppresses errors
if command >/dev/null 2>&1; then

# ✓ Good - errors are visible
if command; then
```

### Test Incrementally
1. Make changes
2. Run locally if possible
3. Commit and push
4. Watch CI for failures
5. Fix issues immediately

### Acceptance Tests
- Should be language-agnostic
- Test the CLI interface, not internals
- Verify consistency between implementations

## Configuration Files

### Document Non-Obvious Decisions
```yaml
# Use v1.1.0+ to avoid API 400 errors
uses: HatsuneMiku3939/direnv-action@v1.1.0
```

```toml
# Normally I don't version-control lock files till later
*.lock
```

### Prefer .gitignore
Don't use runtime exclusions when .gitignore would work better.

### Use Workspace/Monorepo Features
```toml
# Rust workspace
[workspace]
members = ["crate1", "crate2"]

# Node.js workspace
"workspaces": ["packages/*"]
```

## Code Style

### Follow Existing Patterns
Before adding code:
1. Look at neighboring files
2. Check imports and style
3. Use same libraries/patterns
4. Match naming conventions

### Use Standard Formatters
- Rust: `rustfmt`
- Python: `black`, `isort`
- JavaScript/TypeScript: `prettier`
- Run before committing

## Directory Structure

### Multi-Language Projects
```
project/
├── rust/          # Rust implementation
├── python/        # Python implementation
├── js/            # JavaScript implementation
├── tests/         # Shared tests
└── docs/          # Shared documentation
```

### Keep Related Code Together
- Group by feature, not by file type
- Colocate tests with code when possible
- Shared utilities in dedicated directory

## CI/CD Best Practices

### Run Locally First
```bash
# Before pushing, run:
pre-commit run --all-files
./tests/acceptance-test
```

### Fix Immediately
- Don't push "to see what CI says"
- If CI fails, fix before moving on
- Keep main branch green

### Cache Dependencies
Use appropriate caching in CI:
- `cache-dependency-path` for Node.js
- `cache: pip` for Python
- Cargo cache for Rust

## Version Control

### Atomic Commits
- Each commit should be self-contained
- Should not break the build
- Clear, descriptive messages

### Feature Branches
```bash
git checkout -b feature/description
# Work on feature
git push origin feature/description
gh pr create
```

### Clean History
- Squash fixup commits before merge
- Use amend for small fixes
- Keep related changes together

## Documentation

### README Essentials
- Installation instructions
- Basic usage examples
- Development setup
- Contributing guidelines

### Inline Comments
- Explain "why", not "what"
- Document tricky algorithms
- Note assumptions and limitations

## Security

### Never Commit Secrets
- Use environment variables
- Add patterns to .gitignore
- Use secret management tools

### Validate Input
- Sanitize user input
- Validate file paths
- Check array bounds

## Performance

### Measure First
- Profile before optimizing
- Focus on bottlenecks
- Document performance requirements

### Prefer Simple Solutions
- Readable code over clever code
- Standard library over custom implementations
- Well-tested libraries over rolling your own