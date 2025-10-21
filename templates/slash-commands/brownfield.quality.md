# Brownfield Quality

Install linters, formatters, complexity analysis, and pre-commit hooks.

```bash
brownfield quality
```

This command will:
1. Install language-specific linter (pylint, eslint, clippy, golangci-lint)
2. Install formatter (black, prettier, rustfmt, gofmt)
3. Configure complexity analysis (lizard with CCN < 10 threshold)
4. Run security scanner (bandit, npm audit, cargo audit, gosec)
5. Install pre-commit hooks to enforce quality standards
6. Document complexity exceptions if needed

Quality tools installed:
- **Python**: pylint + black + bandit
- **JavaScript**: ESLint + Prettier + npm audit
- **Rust**: clippy + rustfmt + cargo audit
- **Go**: golangci-lint + gofmt + gosec

Pre-commit hooks block commits with:
- Linting errors
- Formatting violations
- Complexity >10 (unless documented)
- Critical security vulnerabilities

Options:
- `--skip-linter` - Skip linter installation
- `--skip-formatter` - Skip formatter installation
- `--skip-hooks` - Skip pre-commit hooks
- `--complexity-threshold N` - Custom complexity threshold (default: 10)
- `--fix-auto` - Auto-fix linter and formatter issues

After completion, validate readiness:
```bash
brownfield validate
```
