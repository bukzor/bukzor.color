# Git Conventions

## Staging Files

### Preferred Patterns
```bash
git add -u              # Stage all modified tracked files
git add <specific>      # Stage specific file(s)
git add .               # Stage everything in current directory
```

### Avoid
```bash
git add -A              # Stages ALL untracked files (often unintended)
```

## Commit Strategy

### New Work
```bash
git commit -m "Clear, descriptive message"
```

### Fixing/Adjusting Existing Work
```bash
git commit --amend --no-edit     # Add to previous commit, keep message
git commit --amend               # Add to previous commit, edit message
```

### When to Amend vs New Commit

**Amend when:**
- Fixing typos or formatting from previous commit
- Adding missing files that belong with previous commit
- Adjusting configuration that was just added
- Iterations on work not yet pushed (or in active PR)

**New commit when:**
- Adding new functionality
- Making substantive changes
- Work has been reviewed/merged
- Creating logical separation for future reverts

## Force Pushing

When you amend commits that have been pushed:
```bash
git push --force-with-lease     # Safer than --force
```

Never use plain `--force` unless absolutely necessary.

## Pull Request Merging

### Default Strategy
```bash
gh pr merge --merge       # Creates merge commit (preferred)
```

### When Specified by Project
```bash
gh pr merge --squash      # Squashes all commits into one
gh pr merge --rebase      # Rebases commits onto base
```

Check project preferences - many maintainers have strong opinions about merge strategy.

## Commit Messages

### Good Patterns
- Start with verb: "Add", "Fix", "Update", "Remove"
- Be specific about what changed
- Include "why" if not obvious
- Reference issues: "Fixes #123"

### Auto-commits from CI
When CI makes commits (e.g., formatting):
```yaml
commit_message: "formatting, from \`pre-commit run --all-files\`"
```

## Checking Status

Always check before committing:
```bash
git status           # See what's changed
git diff            # Review unstaged changes
git diff --staged   # Review staged changes
```

## Branches

```bash
git checkout -b feature-name    # Create and switch to new branch
git checkout main               # Switch to main branch
git branch -d branch-name       # Delete local branch (after merge)
```

## Common Workflows

### Fixing a Mistake in Last Commit
```bash
# Make your fixes
git add -u
git commit --amend --no-edit
git push --force-with-lease
```

### Updating from Main
```bash
git checkout main
git pull
git checkout feature-branch
git rebase main  # or git merge main, depending on preference
```

### Stashing Work
```bash
git stash                  # Save current changes
git stash pop              # Restore saved changes
git stash list             # See all stashes
```