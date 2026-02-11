---
status: active
created: 2025-10-21
updated: 2025-10-21
type: guide
lifecycle: persistent
---

# GitHub Repository Setup Guide

Step-by-step guide to push your BrownKit project to GitHub and create the first release.

---

## Prerequisites

✅ You have a GitHub account
✅ Git is installed locally
✅ You're in the brownfield project directory

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `brownkit` (or your preferred name)
   - **Description**: `AI-driven workflow for transitioning brownfield codebases to Speckit-ready state`
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"
4. Copy the repository URL (e.g., `https://github.com/yourusername/brownkit.git`)

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create brownkit --public --source=. --remote=origin
```

---

## Step 2: Add Remote Repository

After creating the repository on GitHub, add it as a remote:

```bash
# Replace YOUR_USERNAME and REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/brownkit.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/brownkit.git

# Verify remote was added
git remote -v
```

Expected output:
```
origin  https://github.com/YOUR_USERNAME/brownkit.git (fetch)
origin  https://github.com/YOUR_USERNAME/brownkit.git (push)
```

---

## Step 3: Push Your Code

### Current Branch Status

You're currently on branch: `002-brownkit-spec`

### Push Options

#### Option A: Push Feature Branch and Create PR

```bash
# Push your current branch
git push -u origin 002-brownkit-spec

# The -u flag sets upstream tracking
```

After pushing, GitHub will show a link to create a Pull Request. Click it or use:

```bash
# If you have GitHub CLI installed
gh pr create --base main --title "feat: Complete BrownKit v0.1.0 MVP+ implementation" --body "$(cat <<'EOF'
# BrownKit v0.1.0 - Initial Release

This PR introduces the complete BrownKit implementation with all features, tests, and documentation.

## 🎯 What's Included

### Core Features
- ✅ 9 CLI commands (assess, structure, testing, quality, validate, graduate, resume, status, install-completion)
- ✅ 4 language plugins (Python, JavaScript, Rust, Go)
- ✅ 6-phase workflow with state management
- ✅ 7 readiness gates for graduation

### Enhancement Features
- ✅ 7 environment variables for configuration
- ✅ 20+ custom exceptions with suggestions
- ✅ Caching and performance profiling
- ✅ Comprehensive error handling

### Test Infrastructure
- ✅ 4 test fixtures (realistic brownfield projects)
- ✅ 15+ contract tests (plugin interface)
- ✅ 20+ integration tests (end-to-end workflows)
- ✅ Test runner with 8 modes

### Documentation
- ✅ README with examples and CI/CD integration
- ✅ CHANGELOG.md (keep-a-changelog compliant)
- ✅ GitHub workflow guide
- ✅ Testing guide (450+ lines)
- ✅ Implementation validation

## 📊 Statistics
- **Files Changed**: 150 files
- **Lines Added**: 26,257 lines
- **Modules**: 54+ Python modules
- **Tests**: 35+ test cases
- **Documentation**: 2,000+ lines

## ✅ Checklist
- [x] All tests pass
- [x] Documentation complete
- [x] CHANGELOG.md updated
- [x] VERSION file created
- [x] Conventional commit format
- [x] No breaking changes

## 📖 Related Documentation
- See [CHANGELOG.md](CHANGELOG.md) for detailed release notes
- See [PROJECT_STATUS.md](PROJECT_STATUS.md) for feature completion matrix
- See [docs/implementation-validation.md](docs/implementation-validation.md) for compliance verification

## 🚀 Next Steps
After merge:
1. Create tag: `git tag -a v0.1.0 -m "Release version 0.1.0"`
2. Push tag: `git push origin v0.1.0`
3. Create GitHub release with CHANGELOG.md notes
EOF
)"
```

#### Option B: Push Directly to Main (Not Recommended)

If you want to push directly to main (skip PR process):

```bash
# Checkout main branch
git checkout main

# Merge your feature branch
git merge --no-ff 002-brownkit-spec -m "Merge: Complete BrownKit v0.1.0 implementation"

# Push to GitHub
git push -u origin main
```

**⚠️ Warning**: This skips the PR review process. Only do this if you're the sole contributor.

---

## Step 4: Create First Release (After PR Merge)

### Wait for PR Review and Merge

If you created a PR, wait for it to be reviewed and merged. If you're the sole contributor, you can merge it yourself on GitHub.

### After Merge, Create Tag

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create annotated tag for v0.1.0
git tag -a v0.1.0 -m "Release version 0.1.0

Initial release of BrownKit with complete feature set:
- 9 CLI commands for brownfield transformation
- 4 language plugins (Python, JavaScript, Rust, Go)
- 6-phase workflow with state management
- Comprehensive test infrastructure
- Production-ready error handling and caching

See CHANGELOG.md for full details."

# Push the tag
git push origin v0.1.0
```

### Create GitHub Release

#### Option A: Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click "Releases" (right sidebar)
3. Click "Draft a new release"
4. Fill in release details:
   - **Tag**: v0.1.0 (select from dropdown)
   - **Release title**: `BrownKit v0.1.0 - Initial Release`
   - **Description**: Copy from CHANGELOG.md or use this template:

```markdown
# 🎉 BrownKit v0.1.0 - Initial Release

First production-ready release of BrownKit for transforming brownfield codebases into Speckit-ready projects.

## ✨ Features

### Core Functionality
- **9 CLI Commands**: assess, structure, testing, quality, validate, graduate, resume, status, install-completion
- **4 Language Plugins**: Python, JavaScript, Rust, Go with extensible handler interface
- **6-Phase Workflow**: Assessment → Structure → Testing → Quality → Validation → Graduation
- **7 Readiness Gates**: Comprehensive graduation criteria validation

### Enhancement Features
- **Environment Variables**: 7 configuration options for flexible deployment
- **Error Handling**: 20+ custom exceptions with actionable suggestions
- **Performance**: In-memory and disk caching with profiling
- **Shell Completion**: bash, zsh, fish support

### Test Infrastructure
- **Test Fixtures**: 4 realistic brownfield projects
- **Contract Tests**: 15+ plugin interface compliance tests
- **Integration Tests**: 20+ end-to-end workflow tests
- **Test Runner**: Multi-mode script with coverage reporting

## 📦 Installation

```bash
pip install brownkit
```

## 🚀 Quick Start

```bash
# Assess your codebase
brownfield assess --quick

# Generate refactoring plan
brownfield structure

# Add tests and quality gates
brownfield testing
brownfield quality

# Validate and graduate
brownfield validate
brownfield graduate
```

## 📊 Statistics
- **150 files**
- **26,257 lines of code**
- **54+ Python modules**
- **35+ test cases**
- **2,000+ lines of documentation**

## 🔗 Documentation
- [README](https://github.com/YOUR_USERNAME/brownkit/blob/main/README.md)
- [CHANGELOG](https://github.com/YOUR_USERNAME/brownkit/blob/main/CHANGELOG.md)
- [GitHub Workflow Guide](https://github.com/YOUR_USERNAME/brownkit/blob/main/docs/GITHUB_WORKFLOW.md)
- [Testing Guide](https://github.com/YOUR_USERNAME/brownkit/blob/main/tests/README.md)

## 🙏 Acknowledgments
Built with [Claude Code](https://claude.com/claude-code)

---

**Full Changelog**: See [CHANGELOG.md](https://github.com/YOUR_USERNAME/brownkit/blob/main/CHANGELOG.md)
```

5. Click "Publish release"

#### Option B: Using GitHub CLI

```bash
gh release create v0.1.0 \
  --title "BrownKit v0.1.0 - Initial Release" \
  --notes "$(cat CHANGELOG.md)" \
  --generate-notes
```

---

## Step 5: Post-Release Tasks

### Update Repository Settings

1. **About Section**:
   - Add description: "AI-driven workflow for transitioning brownfield codebases to Speckit-ready state"
   - Add topics: `python`, `cli`, `brownfield`, `refactoring`, `speckit`, `code-quality`
   - Add website: Link to documentation (if any)

2. **Branch Protection** (Recommended):
   - Go to Settings → Branches
   - Add rule for `main` branch:
     - ✅ Require pull request reviews before merging
     - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging

3. **Issue Templates**:
   - Create `.github/ISSUE_TEMPLATE/bug_report.md`
   - Create `.github/ISSUE_TEMPLATE/feature_request.md`

4. **PR Template**:
   - Create `.github/pull_request_template.md`

5. **GitHub Actions** (Optional but Recommended):
   - Create `.github/workflows/tests.yml` for automated testing
   - Create `.github/workflows/release.yml` for automated releases

### Enable GitHub Features

- **Discussions**: Settings → Features → Enable Discussions
- **Wikis**: Settings → Features → Enable Wikis (if needed)
- **Projects**: Create project board for issue tracking

### Announce Release

- Post in GitHub Discussions
- Tweet/social media
- Share with community
- Email mailing list (if any)

---

## Troubleshooting

### "Permission denied" when pushing

**Problem**: SSH key not configured or HTTPS authentication failed

**Solution**:
```bash
# Option 1: Use HTTPS with credential manager
git remote set-url origin https://github.com/YOUR_USERNAME/brownkit.git

# Option 2: Configure SSH key
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub:
# Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519.pub

# Use SSH URL
git remote set-url origin git@github.com:YOUR_USERNAME/brownkit.git
```

### "gh: command not found"

**Problem**: GitHub CLI not installed

**Solution**:
```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

### "Branch not found" when creating PR

**Problem**: Branch not pushed to remote yet

**Solution**:
```bash
# Push your branch first
git push -u origin 002-brownkit-spec

# Then create PR
gh pr create --base main --title "feat: Complete BrownKit v0.1.0"
```

---

## Quick Command Reference

```bash
# Setup
git remote add origin https://github.com/YOUR_USERNAME/brownkit.git

# Push branch
git push -u origin 002-brownkit-spec

# Create PR (after push)
gh pr create --base main --title "feat: Complete BrownKit v0.1.0"

# After merge, create tag
git checkout main
git pull
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create release
gh release create v0.1.0 --title "BrownKit v0.1.0" --notes-file CHANGELOG.md
```

---

## Alternative: Manual Workflow Without GitHub CLI

If you don't have `gh` CLI:

1. **Push branch**: `git push -u origin 002-brownkit-spec`
2. **Create PR**: Go to GitHub, click "Compare & pull request" button
3. **Merge PR**: Click "Merge pull request" on GitHub
4. **Create tag**:
   ```bash
   git checkout main
   git pull
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```
5. **Create release**: Go to GitHub → Releases → "Draft a new release"

---

**Last Updated**: 2025-10-21
**Next**: Follow steps above to push to GitHub and create v0.1.0 release!
