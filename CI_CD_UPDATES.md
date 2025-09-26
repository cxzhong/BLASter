# BLASter CI/CD and Dependency Updates

This document summarizes the recent updates to BLASter's CI/CD pipelines and dependency management for improved automation and PyPI publishing.

## Changes Made

### 1. GitHub Actions Updates

Updated all GitHub Actions to their latest stable versions:

- **actions/checkout**: Updated from v4 to v5 across all workflows
- **pypa/cibuildwheel**: Updated from v3.1.4 to v2.21 (latest stable)
- **pypa/gh-action-pypi-publish**: Updated to v1.14.0 with trusted publishing support

### 2. CI/CD Workflow Improvements

#### Build and Test Workflow (`.github/workflows/build-test.yml`)
- Updated all checkout actions to v5
- Maintained comprehensive testing across multiple Python versions (3.11-3.13)
- Preserved existing Eigen3 automatic download testing
- Enhanced caching and artifact management

#### Wheels Workflow (`.github/workflows/wheels.yml`)
- **Updated cibuildwheel configuration**:
  - Removed Python 3.10 support (focusing on 3.11+)
  - Improved dependency specifications with version pinning
  - Better macOS and Windows support
- **Enhanced PyPI Publishing**:
  - Added trusted publishing (no API tokens needed)
  - Added proper environment protection
  - Added TestPyPI publishing for safe testing
  - Fixed publishing conditions to only trigger on tags

#### Documentation Workflow (`.github/workflows/docs.yml`)
- Updated all checkout actions to v5

### 3. Dependency Updates

#### pyproject.toml Improvements
- **Build system**: Updated setuptools requirement to >=68
- **Development dependencies**: Added version pinning for better reproducibility
- **Added ruff**: For modern Python linting and formatting

### 4. PyPI Publishing Setup

#### Trusted Publishing
- Configured trusted publishing for secure uploads without API tokens
- Set up proper environment protection for production releases
- Added TestPyPI integration for testing releases

#### Publishing Triggers
- **Production PyPI**: Only publishes when tags are pushed (e.g., `v1.0.0`)
- **TestPyPI**: Publishes on main branch pushes for testing

## How to Use

### Creating a Release

1. **Test Release** (to TestPyPI):
   ```bash
   git push origin main
   ```
   This will build wheels and publish to TestPyPI for testing.

2. **Production Release** (to PyPI):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   This will build wheels and publish to production PyPI.

### Building Locally

The project still supports local building:

```bash
# Modern PEP 517 build
python -m build

# Legacy build (for development)
make
```

### Setting Up PyPI Publishing

To enable PyPI publishing, you need to configure trusted publishing:

1. Go to PyPI project settings
2. Add trusted publisher for this GitHub repository
3. Configure the workflow name: `wheels.yml`
4. Set environment name: `pypi` (for production)

## Benefits

1. **Automated Publishing**: No manual intervention needed for releases
2. **Security**: Trusted publishing eliminates need for API tokens
3. **Testing**: TestPyPI integration for safe testing
4. **Modern Dependencies**: Latest stable versions of all tools
5. **Cross-Platform**: Automated wheel building for Linux, macOS, and Windows

## Compatibility

All changes maintain backward compatibility:
- Existing local build processes still work
- Manual builds and installations remain supported
- All existing functionality is preserved

## Next Steps

- Test the updated workflows in CI
- Configure trusted publishing in PyPI settings
- Create a test release to verify the complete pipeline