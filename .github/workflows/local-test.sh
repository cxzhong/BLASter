#!/bin/bash

# Local Testing Script for BLASter Workflows
# This script helps test workflow components locally before pushing

set -e

echo "🧪 BLASter Local Testing Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Must be run from BLASter root directory${NC}"
    exit 1
fi

echo "📍 Running from: $(pwd)"
echo ""

# 1. Check Python environment
echo "🐍 Python Environment Check"
echo "----------------------------"
python --version
pip --version
echo ""

# 2. Install development dependencies
echo "📦 Installing Development Dependencies"
echo "-------------------------------------"
pip install --upgrade pip setuptools wheel build
pip install flake8 black isort mypy safety bandit
print_status $? "Development dependencies installed"
echo ""

# 3. Code formatting checks (like in quality.yml)
echo "🎨 Code Formatting Check"
echo "-------------------------"
if command -v black &> /dev/null; then
    black --check --diff src/ examples/ 2>/dev/null
    print_status $? "Code formatting (black)"
else
    print_warning "black not installed, skipping"
fi

if command -v isort &> /dev/null; then
    isort --check-only --diff src/ examples/ 2>/dev/null  
    print_status $? "Import sorting (isort)"
else
    print_warning "isort not installed, skipping"
fi
echo ""

# 4. Linting checks
echo "🔍 Linting Check"
echo "----------------"
if command -v flake8 &> /dev/null; then
    flake8 src/ examples/ --max-line-length=127 --extend-ignore=E203,W503 --statistics
    print_status $? "Linting (flake8)"
else
    print_warning "flake8 not installed, skipping"
fi
echo ""

# 5. Security scan
echo "🔒 Security Scan"
echo "----------------"
if command -v safety &> /dev/null; then
    safety check --json > /tmp/safety-report.json 2>/dev/null || true
    print_status 0 "Security scan (safety)"
else
    print_warning "safety not installed, skipping"
fi

if command -v bandit &> /dev/null; then
    bandit -r src/ -f json -o /tmp/bandit-report.json 2>/dev/null || true
    print_status 0 "Security analysis (bandit)"
else
    print_warning "bandit not installed, skipping"
fi
echo ""

# 6. Build test (like in build-test.yml)
echo "🔨 Build Test"
echo "-------------"
echo "Testing automatic Eigen3 download and build..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/ || true

# Build wheel
python -m build --wheel
print_status $? "Wheel building"

# Check wheel contents
if ls dist/*.whl 1> /dev/null 2>&1; then
    echo "Built wheels:"
    ls -la dist/
    print_status 0 "Wheel files created"
else
    print_status 1 "No wheel files found"
fi
echo ""

# 7. Installation test
echo "📥 Installation Test"
echo "--------------------"
echo "Installing BLASter from built wheel..."

# Install from wheel
if ls dist/*.whl 1> /dev/null 2>&1; then
    pip install dist/*.whl --force-reinstall
    print_status $? "Installation from wheel"
else
    echo "No wheel found, installing in development mode..."
    pip install -e .
    print_status $? "Development installation"
fi
echo ""

# 8. Functionality test (like in build-test.yml)
echo "🧮 Functionality Test"
echo "----------------------"
python -c "
import blaster
import numpy as np
print('✅ BLASter imported successfully')

# Test basic LLL reduction
basis = np.array([[10, 2, 3], [1, 12, 4], [2, 1, 15]])
result = blaster.lll_reduce(basis, verbose=False)

print(f'✅ LLL reduction works: RHF = {result.rhf:.6f}')
print(f'✅ Basis shape: {result.reduced_basis.shape}')
print(f'✅ Transformation verified: {result.verify_transformation()}')

# Test BKZ reduction  
bkz_result = blaster.bkz_reduce(basis, beta=3, verbose=False)
print(f'✅ BKZ reduction works: RHF = {bkz_result.rhf:.6f}')

# Test convenience functions
reduced = blaster.lll(basis, verbose=False)
print(f'✅ Convenience function works: shape = {reduced.shape}')

print('🎉 All functionality tests passed!')
"
print_status $? "Basic functionality test"
echo ""

# 9. Console script test
echo "⚡ Console Script Test"
echo "----------------------"
if command -v blaster &> /dev/null; then
    blaster --help > /dev/null
    print_status $? "Console script (blaster --help)"
else
    print_warning "Console script not available"
fi
echo ""

# 10. Example script test (like in docs.yml)
echo "📚 Example Script Test"
echo "----------------------"
if [ -f "examples/demo.py" ]; then
    python examples/demo.py > /dev/null
    print_status $? "Demo script execution"
else
    print_warning "examples/demo.py not found"
fi
echo ""

# 11. Documentation check
echo "📖 Documentation Check"
echo "----------------------"
docs_ok=0

# Check essential files
for file in "README.md" "INTERFACE_README.md" "LICENSE" "pyproject.toml"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ Missing: $file"
        docs_ok=1
    fi
done

# Check README content
if grep -qi "pip install" README.md; then
    echo "✅ README includes pip installation"
else
    echo "❌ README missing pip installation"
    docs_ok=1
fi

print_status $((1-docs_ok)) "Documentation completeness"
echo ""

# 12. Performance benchmark
echo "🏃 Performance Benchmark"
echo "------------------------"
python -c "
import blaster
import numpy as np
import time

print('Performance test on 8x8 matrix:')
basis = np.random.randint(-10, 11, size=(8, 8))
start = time.time()
result = blaster.lll_reduce(basis, verbose=False)
elapsed = time.time() - start
print(f'Time: {elapsed:.3f}s, RHF: {result.rhf:.6f}')
" 2>/dev/null
print_status $? "Performance benchmark"
echo ""

# Summary
echo "📋 Test Summary"
echo "==============="
echo "Local testing completed! This simulates key parts of the GitHub Actions workflows."
echo ""
echo "Next steps:"
echo "1. Fix any issues found above"
echo "2. Commit your changes"
echo "3. Push to GitHub to trigger full CI/CD workflows"
echo "4. Monitor workflow results in GitHub Actions tab"
echo ""
echo "For release testing:"
echo "- Create a git tag: git tag v1.0.0"
echo "- Push the tag: git push origin v1.0.0"
echo "- This will trigger the release workflow"
echo ""
print_status 0 "Local testing script completed"