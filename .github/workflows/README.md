# GitHub Actions Workflows for BLASter

This directory contains comprehensive CI/CD workflows for the BLASter lattice reduction library.

## 🔧 Workflows Overview

### 1. `build-test.yml` - Build and Test Pipeline
**Triggers:** Push to main/develop, Pull requests, Manual dispatch

**Purpose:** Comprehensive testing across multiple platforms and Python versions

**Key Features:**
- **Matrix Testing:** Tests on Ubuntu, macOS, and Windows with Python 3.10-3.13
- **Automatic Eigen3 Testing:** Validates automatic Eigen3 download without system dependencies
- **Multi-scenario Testing:** Tests different Eigen3 installation scenarios (no-eigen, system-eigen, conda-eigen)
- **Wheel Building:** Creates and tests installable wheels
- **Functionality Testing:** Validates core LLL/BKZ algorithms and Python interface
- **Performance Benchmarks:** Basic performance testing on push to main

**Jobs:**
- `test-build`: Cross-platform matrix testing
- `test-source-distribution`: Source distribution testing  
- `test-eigen3-scenarios`: Eigen3 dependency management validation
- `code-quality`: Basic formatting and linting checks
- `performance-test`: Performance benchmarks (main branch only)
- `documentation`: Documentation completeness validation

### 2. `release.yml` - Release and Publishing Pipeline  
**Triggers:** Version tags (v*.*.*), Manual dispatch

**Purpose:** Automated wheel building and PyPI publishing

**Key Features:**
- **Multi-platform Wheels:** Builds wheels for Linux (x86_64), macOS (x86_64, arm64), Windows (AMD64)
- **Python Version Support:** Python 3.10-3.13 compatibility
- **cibuildwheel Integration:** Professional wheel building with testing
- **Dual Publishing:** Supports both Test PyPI and production PyPI
- **GitHub Releases:** Automatic release creation with assets and changelog
- **Comprehensive Testing:** Tests all artifacts before publishing

**Jobs:**
- `build-wheels`: Multi-platform wheel building with cibuildwheel
- `build-sdist`: Source distribution creation
- `test-release`: Comprehensive artifact testing
- `publish-test-pypi`: Test PyPI publishing (alpha versions or manual)
- `publish-pypi`: Production PyPI publishing (version tags)
- `create-github-release`: GitHub release with assets

### 3. `quality.yml` - Code Quality and Security
**Triggers:** Push to main/develop, Pull requests, Weekly scheduled scans

**Purpose:** Security scanning and code quality analysis

**Key Features:**
- **Security Scanning:** Safety, Bandit, Semgrep vulnerability detection
- **Code Quality:** Advanced linting with pylint, type checking with mypy
- **CodeQL Analysis:** GitHub's advanced security analysis
- **Dependency Auditing:** License checking and vulnerability scanning
- **Complexity Analysis:** Code complexity metrics
- **Automated Reports:** JSON reports uploaded as artifacts

**Jobs:**
- `security-scan`: Multi-tool security vulnerability scanning
- `code-quality`: Advanced code quality analysis (pylint, mypy, complexity)
- `dependency-check`: License and vulnerability auditing of dependencies
- `codeql-analysis`: GitHub CodeQL security analysis  
- `generate-quality-report`: Summary report generation

### 4. `docs.yml` - Documentation and Examples
**Triggers:** Push to main/develop (docs paths), Pull requests, Manual dispatch

**Purpose:** Documentation validation and example testing

**Key Features:**
- **Example Validation:** Tests all example scripts across platforms
- **Documentation Completeness:** Checks for required documentation files
- **Code Block Validation:** Syntax checking of code examples in markdown
- **Performance Benchmarking:** Comprehensive performance characterization
- **Link Checking:** Validates external links in documentation
- **Cross-platform Examples:** Tests examples on Linux, macOS, Windows

**Jobs:**
- `validate-examples`: Cross-platform example script testing
- `check-documentation`: Documentation structure and content validation
- `benchmark-examples`: Comprehensive performance testing and reporting
- `check-links`: Documentation link validation
- `documentation-summary`: Summary report generation

## 🚀 Setup Instructions

### Required Secrets

For the release workflow to publish to PyPI, you need to set up the following secrets in your GitHub repository:

1. **PyPI API Token:**
   ```
   PYPI_API_TOKEN
   ```
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Generate an API token for your project
   - Add it to GitHub Secrets

2. **Test PyPI API Token (Optional):**
   ```
   TEST_PYPI_API_TOKEN  
   ```
   - Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)
   - Generate an API token for testing
   - Add it to GitHub Secrets

### Environments

The workflows use GitHub Environments for additional security:

- `pypi` environment for production PyPI publishing
- `test-pypi` environment for test PyPI publishing

Create these environments in your repository settings and add the respective API tokens.

## 📋 Workflow Features

### Automatic Eigen3 Testing
All workflows specifically test the automatic Eigen3 download feature by intentionally NOT installing system Eigen3 packages. This validates that users can install BLASter without manual dependency management.

### Matrix Testing Strategy
- **Comprehensive Coverage:** Tests key Python versions (3.10-3.13) on major platforms
- **Selective Exclusions:** Reduces CI time while maintaining good coverage
- **Failure Isolation:** `fail-fast: false` ensures all combinations are tested

### Artifact Collection
Workflows automatically collect and upload:
- Built wheels and source distributions
- Security and quality analysis reports  
- Performance benchmarking results
- Documentation validation summaries

### Performance Monitoring
- Automated performance benchmarking on main branch
- Performance characteristics reporting
- Regression detection through consistent testing

## 🔍 Monitoring and Maintenance

### Workflow Status
Monitor workflow status in the "Actions" tab of your GitHub repository.

### Artifact Downloads
All generated reports and build artifacts are available for download from completed workflow runs.

### Scheduled Scans
Security scans run weekly to catch new vulnerabilities in dependencies.

### Manual Triggers
All workflows support manual dispatch for testing and debugging.

## 🛠️ Customization

### Modifying Python Versions
Update the `python-version` matrix in each workflow to add/remove Python versions.

### Platform Support
Modify the `os` matrix to change supported platforms. Note that cibuildwheel in the release workflow controls wheel platforms.

### Security Tools
Add or remove security scanning tools in `quality.yml` based on your needs.

### Performance Thresholds
Modify performance benchmark criteria in the documentation workflow.

## 📚 Best Practices

1. **Branch Protection:** Enable branch protection rules requiring workflow passes
2. **Review Requirements:** Require PR reviews before merging
3. **Status Checks:** Require specific workflows to pass before merging
4. **Automated Releases:** Use semantic versioning for automatic releases
5. **Security Monitoring:** Review security scan results regularly

## 🎯 Workflow Optimization

The workflows are designed for:
- **Fast Feedback:** Critical tests run first
- **Resource Efficiency:** Selective testing matrices
- **Comprehensive Coverage:** Security, quality, functionality, and documentation
- **Professional Standards:** Industry-standard tools and practices

This CI/CD setup ensures BLASter maintains high quality, security, and reliability standards while providing users with seamless installation and usage experience across all supported platforms.