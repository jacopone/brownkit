{ pkgs, lib, config, inputs, ... }:

{
  # Language configuration
  languages.python = {
    enable = true;
    version = "3.11";
    venv.enable = true;
    venv.requirements = ''
      # Core dependencies
      click>=8.1.0
      rich>=13.0.0

      # Development dependencies
      pytest>=7.4.0
      pytest-cov>=4.1.0
      pytest-mock>=3.12.0
      ruff>=0.1.0
      mypy>=1.8.0
    '';
  };

  # System packages available in the shell
  packages = with pkgs; [
    # Python tooling
    python312Packages.lizard  # Complexity analysis (brownfield uses this)

    # Git tooling
    git
    gh  # GitHub CLI for PRs

    # File utilities
    fd     # Fast find alternative
    ripgrep  # Fast grep
    eza    # Better ls
    bat    # Better cat

    # Development utilities
    jq     # JSON processing
    yq-go  # YAML processing
  ];

  # Environment variables
  env = {
    BROWNFIELD_DEBUG = "0";
    PYTHONPATH = "${config.env.DEVENV_ROOT}/src";
  };

  # Scripts available in the shell
  scripts = {
    # Testing
    test.exec = ''
      pytest tests/ -v --tb=short
    '';

    test-cov.exec = ''
      pytest tests/ --cov=src/brownfield --cov-report=html --cov-report=term
      echo "📊 Coverage report generated: htmlcov/index.html"
    '';

    test-watch.exec = ''
      pytest-watch tests/ -v
    '';

    # Code quality
    lint.exec = ''
      echo "🔍 Running ruff check..."
      ruff check src/ tests/
    '';

    lint-fix.exec = ''
      echo "🔧 Running ruff check with auto-fix..."
      ruff check src/ tests/ --fix
    '';

    format.exec = ''
      echo "✨ Formatting code with ruff..."
      ruff format src/ tests/
    '';

    typecheck.exec = ''
      echo "🔎 Running mypy type checker..."
      mypy src/brownfield --ignore-missing-imports
    '';

    # Brownfield commands
    assess-self.exec = ''
      echo "🔍 Running brownfield assess on itself..."
      brownfield assess --quick
    '';

    status-self.exec = ''
      brownfield status
    '';

    # Complexity analysis
    complexity.exec = ''
      echo "📊 Analyzing code complexity..."
      lizard src/brownfield -l python --CCN 10
    '';

    # All quality checks
    check-all.exec = ''
      echo "🚀 Running all quality checks..."
      lint
      format
      typecheck
      test
      complexity
    '';

    # Build and install
    install-dev.exec = ''
      echo "📦 Installing brownfield in editable mode..."
      pip install -e .[dev]
      echo "✅ Brownfield installed! Run: brownfield --help"
    '';

    clean.exec = ''
      echo "🧹 Cleaning up build artifacts..."
      rm -rf build/ dist/ *.egg-info .pytest_cache/ .ruff_cache/ htmlcov/ .coverage
      find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
      echo "✅ Cleaned!"
    '';
  };

  # Pre-commit hooks
  pre-commit.hooks = {
    # Python formatting and linting
    ruff = {
      enable = true;
      name = "ruff";
      entry = "${pkgs.ruff}/bin/ruff check --fix";
      files = "\\.py$";
      language = "system";
    };

    ruff-format = {
      enable = true;
      name = "ruff-format";
      entry = "${pkgs.ruff}/bin/ruff format";
      files = "\\.py$";
      language = "system";
    };

    # Complexity gate
    complexity-check = {
      enable = true;
      name = "complexity-check";
      entry = "${pkgs.python312Packages.lizard}/bin/lizard -l python --CCN 10";
      files = "\\.py$";
      language = "system";
      pass_filenames = true;
    };
  };

  # Shell hook - runs when entering the shell
  enterShell = ''
    # Banner
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║   🎯 BrownKit Development Environment                      ║"
    echo "║                                                            ║"
    echo "║   AI-driven workflow for brownfield → Speckit ready       ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # Auto-install in editable mode
    if [ ! -f ".devenv-initialized" ]; then
      echo "🔧 First-time setup: Installing brownfield in editable mode..."
      pip install -e .[dev] --quiet
      touch .devenv-initialized
      echo "✅ Setup complete!"
      echo ""
    fi

    # Show helpful commands
    echo "📚 Available Commands:"
    echo "  test          - Run test suite"
    echo "  test-cov      - Run tests with coverage report"
    echo "  lint          - Run ruff linter"
    echo "  lint-fix      - Auto-fix linting issues"
    echo "  format        - Format code with ruff"
    echo "  typecheck     - Run mypy type checker"
    echo "  complexity    - Analyze code complexity"
    echo "  check-all     - Run all quality checks"
    echo "  assess-self   - Run brownfield assess on itself"
    echo "  clean         - Clean build artifacts"
    echo ""
    echo "🚀 Quick Start:"
    echo "  brownfield --help              # Show CLI help"
    echo "  brownfield assess --help       # Granular command"
    echo "  brownfield brownfield.assess   # Workflow command"
    echo ""

    # Check git status
    if [ -d .git ]; then
      current_branch=$(git branch --show-current 2>/dev/null)
      if [ -n "$current_branch" ]; then
        echo "📍 Current branch: $current_branch"
      fi
    fi

    echo ""
  '';

  # Process managers (optional, for running background services if needed)
  # processes = {
  #   # Example: Could run a test watcher
  # };
}
