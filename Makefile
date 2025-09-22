# MaScanner Makefile
# Build automation for MaScanner Network Port Scanner

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
SRC_DIR := .
BUILD_DIR := build
DIST_DIR := dist
DOCS_DIR := docs

# Default target
.PHONY: all
all: install

# Help target
.PHONY: help
help:
	@echo "MaScanner Build System"
	@echo "======================"
	@echo ""
	@echo "Available targets:"
	@echo "  install        Install dependencies and setup"
	@echo "  install-dev    Install development dependencies"
	@echo "  run            Run the GUI launcher"
	@echo "  run-basic      Run basic GUI"
	@echo "  run-advanced   Run advanced GUI"
	@echo "  run-cli        Run CLI interface"
	@echo "  test           Run tests"
	@echo "  lint           Run code linting"
	@echo "  format         Format code"
	@echo "  clean          Clean build artifacts"
	@echo "  build          Build distribution packages"
	@echo "  venv           Create virtual environment"
	@echo "  docs           Generate documentation"
	@echo "  package        Create installable package"
	@echo "  uninstall      Remove installation"
	@echo ""
	@echo "Examples:"
	@echo "  make install   # Install MaScanner"
	@echo "  make run       # Run GUI launcher"
	@echo "  make test      # Run tests"

# Installation targets
.PHONY: install
install: check-python check-nmap install-deps
	@echo "Installation completed successfully!"
	@echo "Run 'make run' to start MaScanner"

.PHONY: install-dev
install-dev: install
	$(PIP) install pytest pytest-cov black flake8 mypy sphinx
	@echo "Development dependencies installed"

.PHONY: install-deps
install-deps:
	@echo "Installing Python dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

# Check targets
.PHONY: check-python
check-python:
	@echo "Checking Python installation..."
	@$(PYTHON) --version
	@$(PYTHON) -c "import sys; assert sys.version_info >= (3, 6), 'Python 3.6+ required'"
	@echo "Python check passed"

.PHONY: check-nmap
check-nmap:
	@echo "Checking nmap installation..."
	@command -v nmap >/dev/null 2>&1 || { \
		echo "Error: nmap not found!"; \
		echo "Install nmap:"; \
		echo "  Ubuntu/Debian: sudo apt-get install nmap"; \
		echo "  CentOS/RHEL:   sudo yum install nmap"; \
		echo "  macOS:         brew install nmap"; \
		echo "  Windows:       Download from https://nmap.org/download.html"; \
		exit 1; \
	}
	@nmap --version | head -n1
	@echo "nmap check passed"

.PHONY: check-deps
check-deps:
	@echo "Checking all dependencies..."
	@$(PYTHON) -c "import nmap; print('✓ python-nmap')"
	@$(PYTHON) -c "import tkinter; print('✓ tkinter')"
	@$(PYTHON) -c "import threading; print('✓ threading')"
	@echo "All dependencies available"

# Run targets
.PHONY: run
run: check-deps
	@echo "Starting MaScanner GUI launcher..."
	$(PYTHON) launcher.py

.PHONY: run-basic
run-basic: check-deps
	@echo "Starting MaScanner Basic GUI..."
	$(PYTHON) main.py

.PHONY: run-advanced
run-advanced: check-deps
	@echo "Starting MaScanner Advanced GUI..."
	$(PYTHON) gui_advanced.py

.PHONY: run-cli
run-cli: check-deps
	@echo "Starting MaScanner CLI..."
	$(PYTHON) cli.py --help

# Development targets
.PHONY: test
test:
	@echo "Running tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		$(PYTHON) -m unittest discover tests -v; \
	fi

.PHONY: lint
lint:
	@echo "Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 *.py --max-line-length=120 --ignore=E501,W503; \
	else \
		echo "flake8 not installed, skipping lint"; \
	fi

.PHONY: format
format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black *.py --line-length=120; \
	else \
		echo "black not installed, skipping format"; \
	fi

.PHONY: type-check
type-check:
	@echo "Running type checking..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy *.py --ignore-missing-imports; \
	else \
		echo "mypy not installed, skipping type check"; \
	fi

# Build targets
.PHONY: build
build: clean
	@echo "Building distribution packages..."
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "Build completed in $(DIST_DIR)/"

.PHONY: package
package: build
	@echo "Creating installable package..."
	@mkdir -p $(BUILD_DIR)
	@cp -r $(SRC_DIR)/*.py $(BUILD_DIR)/
	@cp requirements.txt $(BUILD_DIR)/
	@cp README.md $(BUILD_DIR)/
	@cp run_mascanner.sh $(BUILD_DIR)/
	@cp run_mascanner.bat $(BUILD_DIR)/
	@echo "Package created in $(BUILD_DIR)/"

.PHONY: install-package
install-package: build
	@echo "Installing MaScanner package..."
	$(PIP) install $(DIST_DIR)/*.whl
	@echo "Package installed"

# Virtual environment targets
.PHONY: venv
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created in $(VENV)/"
	@echo "Activate with: source $(VENV)/bin/activate (Linux/macOS) or $(VENV)\\Scripts\\activate (Windows)"

.PHONY: venv-install
venv-install: venv
	@echo "Installing in virtual environment..."
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Installation in virtual environment completed"

# Documentation targets
.PHONY: docs
docs:
	@echo "Generating documentation..."
	@mkdir -p $(DOCS_DIR)
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ $(DOCS_DIR)/html/; \
	else \
		echo "Generating simple documentation..."; \
		echo "# MaScanner Documentation" > $(DOCS_DIR)/README.md; \
		cat README.md >> $(DOCS_DIR)/README.md; \
	fi

# Cleaning targets
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Clean completed"

.PHONY: clean-all
clean-all: clean
	@echo "Cleaning everything including virtual environment..."
	rm -rf $(VENV)
	rm -rf $(DOCS_DIR)

# Uninstall target
.PHONY: uninstall
uninstall:
	@echo "Uninstalling MaScanner..."
	$(PIP) uninstall -y mascanner || true
	rm -f $(HOME)/Desktop/MaScanner.desktop
	rm -f /usr/local/bin/mascanner
	@echo "Uninstall completed"

# Testing targets
.PHONY: test-basic
test-basic:
	@echo "Testing basic functionality..."
	$(PYTHON) -c "from scanner import PortScanner; s=PortScanner(); print('Scanner OK')"
	$(PYTHON) -c "import main; print('Basic GUI OK')"

.PHONY: test-advanced
test-advanced:
	@echo "Testing advanced functionality..."
	$(PYTHON) -c "import gui_advanced; print('Advanced GUI OK')"
	$(PYTHON) -c "import utils; print('Utils OK')"

.PHONY: test-cli
test-cli:
	@echo "Testing CLI functionality..."
	$(PYTHON) cli.py --help >/dev/null
	@echo "CLI test passed"

.PHONY: test-all
test-all: test-basic test-advanced test-cli
	@echo "All tests completed"

# Benchmark targets
.PHONY: benchmark
benchmark: check-deps
	@echo "Running performance benchmark..."
	$(PYTHON) -c "
from utils import BenchmarkUtils
from scanner import PortScanner
scanner = PortScanner()
print('Running benchmark on localhost...')
results = BenchmarkUtils.benchmark_scan_performance(scanner)
for config, stats in results.items():
    print(f'{config}: {stats[\"scan_rate\"]:.0f} ports/sec')
"

# Security check targets
.PHONY: security-check
security-check:
	@echo "Running security checks..."
	@$(PYTHON) -c "
from utils import SecurityUtils
privs = SecurityUtils.check_privileges()
print(f'Admin privileges: {privs[\"is_admin\"]}')
print(f'Can run SYN scans: {privs[\"can_syn_scan\"]}')
if not privs['is_admin']:
    print('Note: Some scan types require administrator privileges')
"

# Development workflow targets
.PHONY: dev-setup
dev-setup: venv-install install-dev
	@echo "Development environment setup complete"

.PHONY: dev-test
dev-test: lint type-check test-all
	@echo "Development testing complete"

# Quick start targets
.PHONY: quick-install
quick-install:
	@echo "Quick installation (assumes dependencies are available)..."
	$(PIP) install python-nmap
	@echo "Quick installation complete"

.PHONY: demo
demo: check-deps
	@echo "Running MaScanner demo..."
	@echo "Scanning localhost on common ports..."
	$(PYTHON) cli.py 127.0.0.1 -p 22,80,443 --quiet

# Backup and restore targets
.PHONY: backup-config
backup-config:
	@echo "Backing up configuration..."
	@mkdir -p backups
	@cp -f mascanner_config.json backups/config_backup_$(shell date +%Y%m%d_%H%M%S).json 2>/dev/null || echo "No config to backup"

.PHONY: create-portable
create-portable: build
	@echo "Creating portable version..."
	@mkdir -p portable/mascanner
	@cp *.py portable/mascanner/
	@cp requirements.txt portable/mascanner/
	@cp README.md portable/mascanner/
	@cp run_mascanner.sh portable/mascanner/
	@cp run_mascanner.bat portable/mascanner/
	@echo "#!/bin/bash" > portable/start_mascanner.sh
	@echo "cd mascanner && ./run_mascanner.sh gui" >> portable/start_mascanner.sh
	@chmod +x portable/start_mascanner.sh
	@echo "Portable version created in portable/"

# System integration targets
.PHONY: install-system
install-system: install
	@echo "Installing system-wide..."
	sudo cp run_mascanner.sh /usr/local/bin/mascanner
	sudo chmod +x /usr/local/bin/mascanner
	@echo "System installation complete. Run 'mascanner gui' from anywhere"

# Validation targets
.PHONY: validate
validate: check-python check-nmap check-deps test-basic
	@echo "Validation completed successfully"

# Performance targets
.PHONY: optimize
optimize:
	@echo "Optimizing Python bytecode..."
	$(PYTHON) -O -m compileall .
	@echo "Optimization complete"

# Default error handling
%:
	@echo "Unknown target: $@"
	@echo "Run 'make help' for available targets"
	@exit 1

# Dependencies for targets
install: check-python
install-dev: install
build: clean
test: check-deps
run: install
run-basic: install
run-advanced: install
run-cli: install
