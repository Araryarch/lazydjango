#!/bin/bash
# Local testing script untuk simulasi CI/CD

set -e

echo "🧪 Running LazyDjango Local Tests"
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}📌 Checking Python version...${NC}"
python --version

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -e ".[dev]"

# Check executable
echo -e "${BLUE}🔍 Checking executable...${NC}"
if command -v lazydjango &> /dev/null; then
    echo -e "${GREEN}✓ lazydjango executable found${NC}"
    lazydjango --help > /dev/null
    echo -e "${GREEN}✓ lazydjango runs successfully${NC}"
else
    echo -e "${RED}✗ lazydjango executable not found${NC}"
    exit 1
fi

# Run linting
echo -e "${BLUE}🎨 Running linting...${NC}"
ruff check lazydjango/ || echo -e "${RED}⚠ Ruff found issues${NC}"
black --check lazydjango/ || echo -e "${RED}⚠ Black formatting needed${NC}"

# Run tests
echo -e "${BLUE}🧪 Running tests...${NC}"
pytest --cov=lazydjango --cov-report=term

# Security checks
echo -e "${BLUE}🔒 Running security checks...${NC}"
bandit -r lazydjango/ || echo -e "${RED}⚠ Bandit found issues${NC}"
safety check || echo -e "${RED}⚠ Safety found vulnerabilities${NC}"

# Build check
echo -e "${BLUE}📦 Building package...${NC}"
python -m build

echo -e "${GREEN}✅ All checks completed!${NC}"
