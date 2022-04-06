#!/bin/bash
# LazyDjango Build Script for Unix/Mac

set -e

echo "======================================"
echo "  LazyDjango Build Script"
echo "======================================"

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build UI if Node.js is available
if command -v node &> /dev/null; then
    echo ""
    echo "Building Next.js UI..."
    cd ui
    npm install
    npm run build
    cd ..
    
    # Copy UI to package
    if [ -d "ui/out" ]; then
        rm -rf lazydjango/ui/out
        cp -r ui/out lazydjango/ui/out
        echo "UI copied to lazydjango/ui/out"
    fi
else
    echo "Node.js not found, skipping UI build..."
fi

# Build Python package
echo ""
echo "Building Python package..."
pip install --upgrade pip build twine
python -m build

echo ""
echo "======================================"
echo "  Build Complete!"
echo "======================================"
echo ""
echo "Files in dist/:"
ls -lh dist/

echo ""
echo "To upload to TestPyPI:"
echo "  python -m twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI:"
echo "  python -m twine upload dist/*"
