# BLASter Makefile - supports both legacy and modern PEP 517 build systems
.POSIX:

.PHONY: all build install install-dev cython cython-gdb clean venv-clean eigen3-clean test

# if virtualenv directory venv exists then prefer venv/bin/python3 over system python3
VENV    := venv
PYTHONV := python3
PYTHON  = $(or $(wildcard $(VENV)/bin/$(PYTHONV)), $(shell command -v $(PYTHONV)), $(PYTHONV))


# Default target - build the package
all: build

# Modern PEP 517 build (recommended)
build:
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

# Install in development mode (editable install)
install-dev: 
	$(PYTHON) -m pip install -e .

# Standard installation
install:
	$(PYTHON) -m pip install .

# Legacy build method (backward compatibility)
cython:
	$(PYTHON) setup.py build_ext --inplace

# Debug build (legacy method)
# The LD_PRELOAD trick is from https://github.com/grpc/grpc/issues/25819
cython-gdb:
	$(PYTHON) setup.py build_ext --cython-gdb --inplace

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ cysignals_crash_logs/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.so" -delete
	find . -name "*.c" -path "*/core/*" -delete

# Test the package (if tests exist)
test:
	$(PYTHON) -m pytest tests/ || echo "No tests found or pytest not installed"


### Rules to install Eigen C++ template library for linear algebra locally

# Default version of Eigen C++ template library for linear algebra
EIGEN_VERSION := 3.4.0

eigen3:
	$(MAKE) eigen-$(EIGEN_VERSION)
	if [ -d eigen3 ]; then rm eigen3; fi
	ln -s eigen-$(EIGEN_VERSION) eigen3

eigen-%: eigen-%.tar.gz
	tar -xzvf $< >/dev/null

eigen-%.tar.gz:
	wget -nv "https://gitlab.com/libeigen/eigen/-/archive/$*/$@" -O "$@"

eigen3-clean:
	rm -rf eigen3 eigen-$(EIGEN_VERSION) eigen-$(EIGEN_VERSION).tar.gz



### Rules to create a virtual environment with up-to-date numpy and cython

# Default requirements for modern PEP 517 development
PIP_REQUIREMENTS := pip build wheel cython cysignals numpy setuptools matplotlib pytest

venv:
	@if [ "$(VIRTUAL_ENV)" != "" ]; then echo "Active virtual environment detected. Please run 'deactivate' first!"; false; fi
	$(PYTHON) -m pip install --upgrade pip 2> /dev/null || echo "ERROR: Upgrading pip failed!"
	$(PYTHON) -m pip install virtualenv 2> /dev/null || echo "ERROR: Installing pip package virtualenv failed!"
	$(PYTHON) -m virtualenv $(VENV)
	-@rm activate 2>/dev/null
	ln -s $(VENV)/bin/activate .
	printf "#!/usr/bin/env bash\nOPENBLAS_NUM_THREADS=1 $(VENV)/bin/$(PYTHONV) \$$*\n" > ./$(PYTHONV)
	chmod +x ./$(PYTHONV)
	$(VENV)/bin/$(PYTHONV) -m pip install --upgrade $(PIP_REQUIREMENTS)
	@echo "=================================================================="
	@echo "=== NOTE: Please use 'source activate' to activate environment ==="
	@echo "===       Or use './python3' to use environment                ==="
	@echo "=================================================================="

venv-clean:
	@if [ "$(VIRTUAL_ENV)" != "" ]; then echo "Active virtual environment detected. Please run 'deactivate' first!"; false; fi
	rm -rf venv
