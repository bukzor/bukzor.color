# Claude Tool Usage Patterns

## Bash Tool

### Working Directory Persistence
**Important**: The working directory persists across Bash() tool calls within a conversation.

```python
# ✗ Bad - assumes directory state
Bash("cd rust")
Bash("cargo build")  # May fail if previous command failed

# ✓ Good - use subshells
Bash("(cd rust && cargo build)")

# ✓ Good - avoid cd
Bash("cargo --manifest-path rust/Cargo.toml build")
```

### Command Chaining
```python
# ✓ Good - single tool call
Bash("cmd1 && cmd2 && cmd3")

# ✗ Bad - multiple calls with assumed state
Bash("export VAR=value")
Bash("echo $VAR")  # VAR won't be set
```

### Error Handling
The Bash tool returns error output - check and handle appropriately.

## Read Tool

### Always Read Before Edit
```python
# ✓ Good
Read("file.txt")
Edit("file.txt", old_string="...", new_string="...")

# ✗ Bad - will fail
Edit("file.txt", old_string="guess", new_string="...")
```

### Line Numbers
Line numbers in Read output use the format: `spaces + line number + tab + content`

When using Edit, match content exactly as it appears AFTER the tab.

## Edit Tool

### Exact Matching Required
- `old_string` must match exactly (including whitespace)
- Include enough context to ensure uniqueness
- Use `replace_all=True` for multiple occurrences

### Indentation Preservation
```python
# Read shows: "    4→    def function():"
# The actual content is "    def function():" (4 spaces)

Edit(
    file_path="file.py",
    old_string="    def function():",  # Preserve exact indentation
    new_string="    def new_function():"
)
```

## Write Tool

### Overwrite Warning
Write tool completely replaces file contents. Always use Read first for existing files.

### Creating New Files
```python
# ✓ Good - explicit about creating new file
Write("new_file.txt", content="...")

# For existing files, prefer Edit when possible
```

## Git Operations via Bash

### Check Status First
```python
Bash("git status")
# Review output before staging
Bash("git add -u")
Bash("git commit -m 'message'")
```

### Amending Commits
```python
# For related fixes
Bash("git add -u")
Bash("git commit --amend --no-edit")
Bash("git push --force-with-lease")
```

## Multi-Edit Tool

Use when making multiple changes to the same file:
```python
MultiEdit(
    file_path="file.py",
    edits=[
        {"old_string": "...", "new_string": "..."},
        {"old_string": "...", "new_string": "..."}
    ]
)
```

## WebSearch and WebFetch

### WebSearch for Research
```python
WebSearch("query terms")  # Returns search results
```

### WebFetch for Specific Pages
```python
WebFetch(
    url="https://...",
    prompt="Extract the installation instructions"
)
```

## TodoWrite Tool

### When to Use
- Complex multi-step tasks
- Tasks requiring careful planning
- Multiple related operations
- Tracking progress through long conversations

### Status Management
```python
TodoWrite(todos=[
    {"content": "Task 1", "status": "completed", "activeForm": "Completing Task 1"},
    {"content": "Task 2", "status": "in_progress", "activeForm": "Working on Task 2"},
    {"content": "Task 3", "status": "pending", "activeForm": "Planning Task 3"}
])
```

Only one task should be `in_progress` at a time.

## General Best Practices

1. **Batch Related Operations**: Use single tool calls when possible
2. **Verify Before Acting**: Read files, check status, then modify
3. **Handle Errors**: Check tool results and adapt
4. **Preserve Context**: Include enough information for unique matches
5. **Avoid State Assumptions**: Don't assume previous commands succeeded
6. **Use Appropriate Tools**: Choose the right tool for the task