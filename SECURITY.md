# Security Policy

## Supported Versions

We release security updates for the following versions of BrownKit:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in BrownKit, please report it privately:

### Email

Send details to: **security@brownkit.dev**

### What to Include

Please include the following information in your report:

- **Description**: Brief overview of the vulnerability
- **Impact**: What an attacker could achieve
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are vulnerable
- **Proof of Concept**: Code or screenshots demonstrating the issue (if applicable)
- **Suggested Fix**: If you have ideas for how to fix it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Target**: Within 30 days for critical issues, 90 days for others

### Our Process

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Assessment**: We'll investigate and assess the severity
3. **Fix Development**: We'll develop and test a fix
4. **Disclosure**: We'll coordinate disclosure timing with you
5. **Release**: We'll release a security patch
6. **Credit**: We'll credit you in the release notes (if desired)

## Security Best Practices

When using BrownKit, follow these security best practices:

### 1. Review Generated Plans

BrownKit generates refactoring plans but does NOT automatically execute them. Always:

- ✅ Review all suggested changes before applying
- ✅ Understand the impact of structural changes
- ✅ Test in a non-production environment first
- ✅ Commit changes incrementally for easy rollback

### 2. Use Version Control

BrownKit requires Git repositories:

- ✅ Commit before running BrownKit commands
- ✅ Review diffs before committing BrownKit changes
- ✅ Use feature branches for brownfield transformation
- ✅ Never force push to main/master branches

### 3. Protect Sensitive Information

- ✅ Ensure `.gitignore` excludes secrets before using BrownKit
- ✅ Review assessment reports for exposed credentials
- ✅ Use BrownKit's security scanning features
- ✅ Never commit `.specify/memory/` to public repositories (contains state files)

### 4. Environment Isolation

- ✅ Use virtual environments (venv, conda, or devenv)
- ✅ Run BrownKit in isolated development environments
- ✅ Do NOT run BrownKit directly on production systems
- ✅ Test in staging before applying to main branches

### 5. Dependency Security

- ✅ Keep BrownKit updated to latest version
- ✅ Review BrownKit's dependencies regularly
- ✅ Use `pip audit` or similar tools to scan for vulnerabilities
- ✅ Monitor security advisories for Python ecosystem

### 6. Tool Installation

BrownKit installs language-specific tools (pytest, eslint, etc.):

- ✅ Review tool versions being installed
- ✅ Use trusted package registries (PyPI, npm, crates.io)
- ✅ Verify checksums when possible
- ✅ Use lockfiles to pin dependency versions

## Known Security Considerations

### By Design

**Human-in-the-Loop Refactoring**: BrownKit does NOT automatically refactor code. This is intentional to prevent destructive automation. All structural changes require manual review and approval.

**Git Operations**: BrownKit performs Git operations (commit, status, diff). It:
- ✅ Never force pushes
- ✅ Never pushes to remote without explicit user command
- ✅ Creates atomic commits for reversibility
- ✅ Uses safe Git patterns

**File System Access**: BrownKit reads and writes files in your project:
- ✅ Only operates within specified project root
- ✅ Respects `.gitignore` patterns
- ✅ Creates backups before modifications (where applicable)
- ✅ Never deletes files without confirmation

### Security Scanning

BrownKit integrates with security tools:

- **Python**: `bandit` for security linting
- **JavaScript**: `npm audit` for dependency scanning
- **Rust**: `cargo audit` for vulnerability detection
- **Go**: `gosec` for security analysis

These tools may report false positives. Always review findings before acting.

## Vulnerability Disclosure Policy

### Coordinated Disclosure

We believe in coordinated vulnerability disclosure:

1. **Private Reporting**: Report vulnerabilities privately first
2. **Fix Development**: We work with you to develop a fix
3. **Coordinated Announcement**: We coordinate public disclosure timing
4. **Credit**: We acknowledge your contribution (if desired)

### Public Disclosure Timeline

- **Critical Vulnerabilities**: Public disclosure after fix is released
- **High Severity**: 30 days after initial report (or fix release, whichever comes first)
- **Medium/Low Severity**: 90 days after initial report

We may disclose earlier if:
- The vulnerability is already publicly known
- Active exploitation is detected
- You request earlier disclosure

## Security Updates

Security updates are released as:

- **Patch Releases**: `0.2.1`, `0.2.2` (backwards-compatible security fixes)
- **Advisory**: Published on GitHub Security Advisories
- **Changelog**: Documented in CHANGELOG.md with `[SECURITY]` tag

Subscribe to releases to receive security notifications:
- GitHub: Watch → Custom → Releases
- RSS: `https://github.com/jacopone/brownkit/releases.atom`

## Security Hall of Fame

We acknowledge security researchers who responsibly disclose vulnerabilities:

- *No vulnerabilities reported yet*

If you report a vulnerability, we'll credit you here (with your permission).

## Contact

- **Security Issues**: security@brownkit.dev
- **General Support**: support@brownkit.dev
- **GitHub Issues**: For non-security bugs only

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [npm Security](https://docs.npmjs.com/auditing-package-dependencies-for-security-vulnerabilities)

---

**Last Updated**: 2025-10-23

Thank you for helping keep BrownKit and its users safe!
