---
status: active
created: 2025-10-21
updated: 2025-10-21
type: guide
lifecycle: persistent
---

# GitHub Workflow & Release Management Guide

Comprehensive guide for managing BrownKit development using GitHub features and industry best practices.

---

## Table of Contents

1. [Semantic Versioning](#semantic-versioning)
2. [Git Branching Strategy](#git-branching-strategy)
3. [Commit Message Convention](#commit-message-convention)
4. [GitHub Issues & Projects](#github-issues--projects)
5. [Pull Request Workflow](#pull-request-workflow)
6. [Release Process](#release-process)
7. [Changelog Management](#changelog-management)
8. [GitHub Actions CI/CD](#github-actions-cicd)
9. [Milestones & Roadmap](#milestones--roadmap)
10. [Community Management](#community-management)

---

## Semantic Versioning

### Version Format: `MAJOR.MINOR.PATCH`

BrownKit follows [Semantic Versioning 2.0.0](https://semver.org/):

#### MAJOR version (X.0.0)
Increment when making **incompatible API changes**:
- Breaking CLI command changes
- Removed functionality
- Changed default behavior that breaks existing workflows
- Incompatible configuration file format

**Example**: `1.0.0 → 2.0.0`
```
BREAKING CHANGE: Renamed `brownfield assess` to `brownfield analyze`
```

#### MINOR version (0.X.0)
Increment when adding **new functionality** (backwards-compatible):
- New CLI commands
- New language plugins
- New configuration options
- Enhanced features

**Example**: `0.1.0 → 0.2.0`
```
feat: Add TypeScript language plugin support
feat: Add --watch mode for continuous assessment
```

#### PATCH version (0.0.X)
Increment for **bug fixes** (backwards-compatible):
- Bug fixes
- Documentation improvements
- Performance improvements (no API changes)
- Dependency updates

**Example**: `0.1.0 → 0.1.1`
```
fix: Correct Python version detection for 3.12+
docs: Update README with Windows installation steps
```

### Pre-release Versions

Use pre-release identifiers for development:

- **Alpha**: `0.2.0-alpha.1` - Early testing, unstable
- **Beta**: `0.2.0-beta.1` - Feature-complete, testing
- **RC**: `0.2.0-rc.1` - Release candidate, final testing

---

## Git Branching Strategy

### Main Branches

#### `main` (or `master`)
- **Purpose**: Production-ready code
- **Protection**: Protected branch, requires PR reviews
- **Releases**: All releases tagged from this branch
- **Rule**: Never commit directly to main

#### `develop`
- **Purpose**: Integration branch for features
- **Protection**: Requires PR, automated tests must pass
- **Merges**: Features merge here first, then to main

### Supporting Branches

#### Feature Branches: `feature/<description>`
- **Purpose**: New features or enhancements
- **Naming**: `feature/typescript-plugin`, `feature/watch-mode`
- **Branch from**: `develop`
- **Merge to**: `develop`
- **Lifetime**: Temporary, deleted after merge

**Example**:
```bash
git checkout develop
git checkout -b feature/typescript-plugin

# Work on feature...
git add .
git commit -m "feat: Add TypeScript language plugin"

# Push and create PR to develop
git push origin feature/typescript-plugin
```

#### Bugfix Branches: `bugfix/<issue-number>-<description>`
- **Purpose**: Bug fixes for develop branch
- **Naming**: `bugfix/123-python-detection-error`
- **Branch from**: `develop`
- **Merge to**: `develop`

**Example**:
```bash
git checkout develop
git checkout -b bugfix/123-python-detection-error

# Fix bug...
git commit -m "fix: Correct Python 3.12 version detection (#123)"

git push origin bugfix/123-python-detection-error
```

#### Hotfix Branches: `hotfix/<version>`
- **Purpose**: Critical fixes for production
- **Naming**: `hotfix/0.1.1`
- **Branch from**: `main`
- **Merge to**: `main` AND `develop`
- **Tag**: Create version tag after merge

**Example**:
```bash
git checkout main
git checkout -b hotfix/0.1.1

# Fix critical bug...
git commit -m "fix: Prevent data loss in structure verification"

# Merge to main
git checkout main
git merge --no-ff hotfix/0.1.1
git tag -a v0.1.1 -m "Hotfix: Data loss prevention"
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/0.1.1
git push origin develop

# Delete hotfix branch
git branch -d hotfix/0.1.1
```

#### Release Branches: `release/<version>`
- **Purpose**: Prepare for production release
- **Naming**: `release/0.2.0`
- **Branch from**: `develop`
- **Merge to**: `main` AND `develop`
- **Activities**: Version bumps, changelog updates, final testing

**Example**:
```bash
git checkout develop
git checkout -b release/0.2.0

# Update version
echo "0.2.0" > VERSION
git add VERSION

# Update changelog
# Edit CHANGELOG.md to move [Unreleased] to [0.2.0]
git add CHANGELOG.md
git commit -m "chore: Bump version to 0.2.0"

# Final testing...
./scripts/run_tests.sh all

# Merge to main
git checkout main
git merge --no-ff release/0.2.0
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/0.2.0
git push origin develop

# Delete release branch
git branch -d release/0.2.0
```

### Branching Diagram

```
main     ─────────────────●─────────────────●─────────
                           │                 │
                          v0.1.0           v0.2.0
                           │                 │
develop  ───────●─────────●────●────●───────●─────────
                │               │    │
feature/A  ─────●──────────┘    │    │
                                │    │
bugfix/123  ────────────────────●────┘
```

---

## Commit Message Convention

### Format: Conventional Commits

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | Description | Changelog Section | Example |
|------|-------------|-------------------|---------|
| `feat` | New feature | ✨ Added | `feat(cli): Add --watch mode for continuous assessment` |
| `fix` | Bug fix | 🐛 Fixed | `fix(python): Correct version detection for 3.12+` |
| `docs` | Documentation | 📝 Documentation | `docs(readme): Add Windows installation guide` |
| `style` | Code style (no logic change) | - | `style: Format code with black` |
| `refactor` | Code refactoring | - | `refactor(plugins): Extract common handler logic` |
| `perf` | Performance improvement | ⚡ Performance | `perf(cache): Use faster hashing algorithm` |
| `test` | Add/update tests | - | `test(contract): Add tests for new plugin interface` |
| `chore` | Maintenance | - | `chore: Update dependencies` |
| `ci` | CI/CD changes | - | `ci: Add GitHub Actions workflow` |
| `build` | Build system | - | `build: Update pyproject.toml` |
| `revert` | Revert previous commit | - | `revert: "feat: Add watch mode"` |

### Scopes (Optional)

- `cli` - CLI commands
- `plugins` - Language plugins
- `assessment` - Assessment engine
- `remediation` - Remediation modules
- `state` - State management
- `docs` - Documentation
- `tests` - Test infrastructure

### Subject Guidelines

- Use imperative mood ("Add feature" not "Added feature")
- No period at the end
- Max 72 characters
- Lowercase first letter (except proper nouns)

### Body (Optional)

- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Separate from subject with blank line

### Footer (Optional)

- **Breaking changes**: `BREAKING CHANGE: <description>`
- **Issue references**: `Closes #123`, `Fixes #456`
- **Co-authors**: `Co-authored-by: Name <email>`

### Examples

#### Feature Commit
```
feat(plugins): Add TypeScript language plugin support

Implements full TypeScript support including:
- ts-node detection
- jest integration for TypeScript
- eslint-typescript configuration
- tsconfig.json validation

This enables brownfield analysis of TypeScript projects
with full type-checking integration.

Closes #45
```

#### Bug Fix Commit
```
fix(python): Correct version detection for Python 3.12+

Python 3.12 changed the sys.version format which broke
our regex-based detection. Updated to use
platform.python_version() instead.

Fixes #123
```

#### Breaking Change Commit
```
feat(cli)!: Rename assess command to analyze

BREAKING CHANGE: The `brownfield assess` command has been
renamed to `brownfield analyze` for clarity and consistency
with industry terminology.

Migration:
  Before: brownfield assess --quick
  After:  brownfield analyze --quick

Closes #200
```

### Atomic Commits

Each commit should be a **single logical change**:

✅ **Good**:
```bash
git commit -m "feat(python): Add Python 3.12 support"
git commit -m "test(python): Add tests for Python 3.12 detection"
git commit -m "docs(readme): Document Python 3.12 compatibility"
```

❌ **Bad**:
```bash
git commit -m "Add Python 3.12 support, tests, and update docs"
```

---

## GitHub Issues & Projects

### Issue Types

Use issue templates for consistency:

#### Bug Report
```markdown
**Description**
Clear description of the bug

**To Reproduce**
1. Run `brownfield assess`
2. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Ubuntu 22.04
- Python: 3.11
- BrownKit: 0.1.0

**Additional Context**
Screenshots, logs, etc.
```

#### Feature Request
```markdown
**Is your feature related to a problem?**
Clear description of the problem

**Proposed Solution**
Describe your solution

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, etc.
```

#### Enhancement
```markdown
**Current Behavior**
How it works now

**Improved Behavior**
How it should work

**Benefits**
Why this improvement matters

**Implementation Notes**
Technical details, if any
```

### Labels

#### Type Labels
- `bug` 🐛 - Something isn't working
- `feature` ✨ - New feature request
- `enhancement` 💡 - Improvement to existing feature
- `documentation` 📝 - Documentation improvements
- `performance` ⚡ - Performance improvements

#### Priority Labels
- `priority: critical` 🔴 - Must fix immediately
- `priority: high` 🟠 - Fix soon
- `priority: medium` 🟡 - Fix eventually
- `priority: low` 🟢 - Nice to have

#### Status Labels
- `status: needs-triage` - Needs review
- `status: blocked` - Blocked by dependency
- `status: in-progress` - Currently being worked on
- `status: needs-review` - PR ready for review

#### Other Labels
- `good first issue` - Good for newcomers
- `help wanted` - Community help requested
- `question` - Question about usage
- `wontfix` - Will not be fixed
- `duplicate` - Duplicate of another issue

### Projects (GitHub Projects)

#### Project Boards

**1. Kanban Board (for ongoing work)**
```
📋 Backlog → 🏗️ In Progress → 👀 Review → ✅ Done
```

**2. Roadmap (for planning)**
```
🎯 v0.2.0 | 🎯 v0.3.0 | 🎯 v1.0.0
```

**3. Bug Tracker**
```
🐛 Reported → 🔍 Investigating → 🔧 Fixing → ✅ Fixed
```

#### Milestones

Create milestones for each version:

**Milestone: v0.2.0**
- **Due date**: 2025-12-01
- **Description**: TypeScript support and performance improvements
- **Issues**: Link all v0.2.0 issues

---

## Pull Request Workflow

### PR Title Format

Use conventional commit format:
```
feat(plugins): Add TypeScript language plugin
fix(python): Correct version detection for 3.12+
```

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Added TypeScript plugin
- Updated documentation
- Added tests

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass (`./scripts/run_tests.sh`)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style (black, pylint)
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Additional Notes
[Any additional context]
```

### PR Review Process

1. **Author** creates PR with description
2. **Automated checks** run (tests, linting)
3. **Reviewers** assigned (1-2 people)
4. **Review** comments and suggestions
5. **Author** addresses feedback
6. **Approval** from required reviewers
7. **Merge** using "Squash and merge" or "Merge commit"

### PR Review Guidelines

**For Reviewers**:
- ✅ Check code quality and style
- ✅ Verify tests are comprehensive
- ✅ Ensure documentation is updated
- ✅ Test locally if needed
- ✅ Be constructive and respectful

**For Authors**:
- ✅ Keep PRs focused and small (<500 lines)
- ✅ Respond to feedback promptly
- ✅ Add tests for new features
- ✅ Update documentation
- ✅ Squash commits before merge

---

## Release Process

### Step-by-Step Release Guide

#### 1. Preparation Phase

```bash
# Checkout develop and update
git checkout develop
git pull origin develop

# Create release branch
git checkout -b release/0.2.0
```

#### 2. Version Bump

```bash
# Update VERSION file
echo "0.2.0" > VERSION

# Update version in pyproject.toml
# [tool.poetry]
# version = "0.2.0"

# Update version in src/brownfield/cli/commands.py
# @click.version_option(version="0.2.0", prog_name="brownkit")
```

#### 3. Update CHANGELOG.md

Move `[Unreleased]` items to `[0.2.0] - 2025-10-21`:

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

### Changed
- Improved cache performance
```

#### 4. Commit Changes

```bash
git add VERSION pyproject.toml CHANGELOG.md src/brownfield/cli/commands.py
git commit -m "chore: Bump version to 0.2.0"
```

#### 5. Final Testing

```bash
# Run full test suite
./scripts/run_tests.sh coverage

# Manual smoke test
pip install -e .
brownfield --version  # Should show 0.2.0
brownfield assess --help
```

#### 6. Merge to Main

```bash
# Merge to main
git checkout main
git merge --no-ff release/0.2.0 -m "Release version 0.2.0"

# Create tag
git tag -a v0.2.0 -m "Release version 0.2.0

## Changes in this release:
- Added TypeScript language plugin
- Added watch mode for continuous assessment
- Fixed Python 3.12 detection issue
- Improved cache performance

See CHANGELOG.md for full details."

# Push main and tag
git push origin main
git push origin v0.2.0
```

#### 7. Merge Back to Develop

```bash
git checkout develop
git merge --no-ff release/0.2.0
git push origin develop
```

#### 8. Create GitHub Release

Go to GitHub → Releases → Draft a new release:

**Tag**: v0.2.0
**Title**: BrownKit v0.2.0 - TypeScript Support & Performance
**Description**:
```markdown
## 🎉 What's New in v0.2.0

### ✨ Added
- **TypeScript Plugin** - Full support for TypeScript projects
- **Watch Mode** - Continuous assessment with `--watch` flag
- **Performance Improvements** - 2x faster cache operations

### 🐛 Fixed
- Python 3.12 version detection (#123)
- Structure verification edge cases (#145)

### 📊 Metrics
- 45 commits since v0.1.0
- 12 contributors
- 15 issues closed

### 📦 Installation

```bash
pip install brownkit==0.2.0
```

### 🔗 Links
- [Full Changelog](https://github.com/brownkit/brownkit/blob/main/CHANGELOG.md)
- [Documentation](https://brownkit.readthedocs.io)

### 🙏 Contributors
Thank you to all contributors who made this release possible!
```

**Assets**: Upload distribution files (if applicable)

#### 9. Announce Release

- Post on GitHub Discussions
- Update documentation site
- Tweet/social media announcement
- Email mailing list

#### 10. Cleanup

```bash
# Delete release branch
git branch -d release/0.2.0
git push origin --delete release/0.2.0
```

---

## Changelog Management

### Structure

```markdown
# Changelog

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.0] - 2025-10-21
### Added
- Feature X
### Fixed
- Bug Y

## [0.1.0] - 2025-10-21
Initial release
```

### Categories

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

### Best Practices

✅ **Do**:
- Write for users, not developers
- Use present tense ("Add feature" not "Added feature")
- Link to issues/PRs
- Group related changes
- Date each release

❌ **Don't**:
- Use technical jargon
- Include implementation details
- List every commit
- Forget to update before release

---

## GitHub Actions CI/CD

### Recommended Workflows

#### `.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install -e .

      - name: Run tests
        run: ./scripts/run_tests.sh coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

#### `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

---

## Milestones & Roadmap

### Public Roadmap

Create `ROADMAP.md`:

```markdown
# BrownKit Roadmap

## v0.2.0 (Q4 2025)
- [ ] TypeScript plugin
- [ ] Watch mode
- [ ] Performance improvements

## v0.3.0 (Q1 2026)
- [ ] Java plugin
- [ ] C++ plugin
- [ ] GUI mode

## v1.0.0 (Q2 2026)
- [ ] Stable API
- [ ] Full documentation
- [ ] 1000+ projects transformed
```

---

## Community Management

### GitHub Discussions

Enable Discussions for:
- **Announcements** - Release notes, updates
- **Q&A** - User questions
- **Ideas** - Feature suggestions
- **Show and Tell** - User projects

### Contributing Guidelines

Create `CONTRIBUTING.md` with:
- Code of Conduct
- Development setup
- Testing requirements
- PR process
- Style guide

### Security Policy

Create `SECURITY.md`:
```markdown
# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability
Email security@brownkit.dev
```

---

## Quick Reference

### Common Commands

```bash
# Create feature branch
git checkout -b feature/my-feature develop

# Commit with conventional format
git commit -m "feat(scope): Add new feature"

# Create PR
gh pr create --base develop --title "feat: Add new feature"

# Tag release
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0

# Create GitHub release
gh release create v0.2.0 --generate-notes
```

### Version Bump Checklist

- [ ] Update VERSION file
- [ ] Update pyproject.toml
- [ ] Update CLI version option
- [ ] Update CHANGELOG.md
- [ ] Run tests
- [ ] Create tag
- [ ] Push to GitHub
- [ ] Create GitHub release
- [ ] Announce

---

**Last Updated**: 2025-10-21
**Maintainer**: BrownKit Team
