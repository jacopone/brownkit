---
status: active
created: 2025-10-21
updated: 2025-10-21
type: guide
lifecycle: persistent
---

# Quick Start: GitHub & Version Management

Quick reference for managing BrownKit using GitHub best practices.

---

## 📚 Essential Reading

1. **CHANGELOG.md** - Track all changes (based on keepachangelog.com)
2. **docs/GITHUB_WORKFLOW.md** - Complete workflow guide
3. **VERSION** - Current version number (semantic versioning)

---

## 🚀 Common Workflows

### Creating a New Feature

```bash
# 1. Checkout develop and update
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Make changes...
# Edit files, add code

# 4. Commit with conventional format
git add .
git commit -m "feat(scope): Add my new feature

Detailed description of what was added.

Closes #123"

# 5. Push and create PR
git push origin feature/my-new-feature
gh pr create --base develop --title "feat: Add my new feature"
```

### Fixing a Bug

```bash
# 1. Create bugfix branch
git checkout develop
git checkout -b bugfix/42-fix-assessment-error

# 2. Fix the bug...
# Edit files

# 3. Commit
git commit -m "fix(assessment): Correct Python version detection

Fixed regex pattern to handle Python 3.12+ versions.

Fixes #42"

# 4. Push and create PR
git push origin bugfix/42-fix-assessment-error
gh pr create --base develop --title "fix: Correct Python version detection"
```

---

## 🏷️ Version Management

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features (backwards-compatible)
- **PATCH** (0.1.1): Bug fixes (backwards-compatible)

### When to Bump Which Number?

| Change Type | Example | Bump |
|-------------|---------|------|
| Breaking change | Rename CLI command | MAJOR |
| New feature | Add new language plugin | MINOR |
| Bug fix | Fix detection error | PATCH |
| Documentation | Update README | PATCH |
| Performance | Optimize cache | MINOR/PATCH |

---

## 📝 Commit Message Format

### Template

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (no logic change)
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `test` - Add/update tests
- `chore` - Maintenance

### Examples

```bash
# Simple feature
git commit -m "feat(plugins): Add TypeScript plugin"

# Bug fix with issue reference
git commit -m "fix(python): Correct version detection (#42)"

# Breaking change
git commit -m "feat(cli)!: Rename assess to analyze

BREAKING CHANGE: Command renamed for clarity.
Migration: Use 'brownfield analyze' instead of 'brownfield assess'"

# Documentation
git commit -m "docs(readme): Add installation instructions"
```

---

## 🎯 Release Process (Step-by-Step)

### Preparation

```bash
# 1. Checkout develop
git checkout develop
git pull origin develop

# 2. Create release branch
git checkout -b release/0.2.0
```

### Version Bump

```bash
# 3. Update version files
echo "0.2.0" > VERSION

# Update pyproject.toml
# [tool.poetry]
# version = "0.2.0"

# Update src/brownfield/cli/commands.py
# @click.version_option(version="0.2.0", ...)
```

### Update Changelog

Edit `CHANGELOG.md`:

```markdown
## [Unreleased]

### Planned
- Future features...

## [0.2.0] - 2025-10-21

### Added
- TypeScript language plugin
- Watch mode for continuous assessment

### Fixed
- Python 3.12 detection issue
```

### Commit and Test

```bash
# 4. Commit version bump
git add VERSION pyproject.toml CHANGELOG.md src/brownfield/cli/commands.py
git commit -m "chore: Bump version to 0.2.0"

# 5. Run tests
./scripts/run_tests.sh coverage
```

### Merge and Tag

```bash
# 6. Merge to main
git checkout main
git merge --no-ff release/0.2.0 -m "Release version 0.2.0"

# 7. Create tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# 8. Push
git push origin main
git push origin v0.2.0

# 9. Merge back to develop
git checkout develop
git merge --no-ff release/0.2.0
git push origin develop

# 10. Delete release branch
git branch -d release/0.2.0
```

### Create GitHub Release

```bash
# Using GitHub CLI
gh release create v0.2.0 \
  --title "BrownKit v0.2.0" \
  --notes "See CHANGELOG.md for details" \
  --generate-notes
```

---

## 🌳 Branch Strategy

### Permanent Branches

- **main** - Production-ready code (protected)
- **develop** - Integration branch for features

### Temporary Branches

- **feature/*** - New features
- **bugfix/*** - Bug fixes
- **hotfix/*** - Critical production fixes
- **release/*** - Release preparation

### Branch Naming

```
feature/typescript-plugin
bugfix/42-python-detection
hotfix/0.1.1
release/0.2.0
```

---

## 🔖 GitHub Labels

### Priority

- `priority: critical` 🔴
- `priority: high` 🟠
- `priority: medium` 🟡
- `priority: low` 🟢

### Type

- `bug` 🐛
- `feature` ✨
- `enhancement` 💡
- `documentation` 📝

### Status

- `status: in-progress`
- `status: needs-review`
- `status: blocked`

---

## 📋 Changelog Management

### Structure

```markdown
# Changelog

## [Unreleased]
### Added
### Changed
### Fixed

## [0.2.0] - 2025-10-21
### Added
- Feature X

## [0.1.0] - 2025-10-21
Initial release
```

### Best Practices

✅ **Do**:
- Write for users, not developers
- Link to issues (#123)
- Group related changes
- Date each release

❌ **Don't**:
- Use technical jargon
- List every commit
- Forget to update before release

---

## 🤖 GitHub Actions

### Essential Workflows

Create `.github/workflows/tests.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-dev.txt
      - run: ./scripts/run_tests.sh coverage
```

---

## 🎓 Learning Resources

### Semantic Versioning
https://semver.org/

### Conventional Commits
https://www.conventionalcommits.org/

### Keep a Changelog
https://keepachangelog.com/

### Git Flow
https://nvie.com/posts/a-successful-git-branching-model/

---

## 📞 Quick Commands

```bash
# Status
git status
gh pr status
gh issue list

# Create PR
gh pr create --base develop --title "feat: Add feature"

# Create issue
gh issue create --title "Bug: Description" --label bug

# Create release
gh release create v0.2.0 --generate-notes

# View changelog
cat CHANGELOG.md

# Current version
cat VERSION
```

---

## 🎯 Checklist: Before Release

- [ ] All tests pass
- [ ] VERSION file updated
- [ ] pyproject.toml version updated
- [ ] CLI version option updated
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] No uncommitted changes
- [ ] Tag created and pushed
- [ ] GitHub release created
- [ ] Release announced

---

## 💡 Tips

### Atomic Commits
Make small, focused commits that do one thing well.

### Meaningful Messages
Write commit messages that explain **why**, not **what**.

### Frequent Pushes
Push to remote often to backup work and enable collaboration.

### Review PRs
Always review your own PRs before requesting review from others.

### Update Often
Regularly pull from develop to avoid merge conflicts.

---

**Last Updated**: 2025-10-21
**Quick Help**: See `docs/GITHUB_WORKFLOW.md` for detailed guide
