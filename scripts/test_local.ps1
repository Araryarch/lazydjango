# Local testing script untuk Windows PowerShell

Write-Host "🧪 Running LazyDjango Local Tests" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check Python version
Write-Host "📌 Checking Python version..." -ForegroundColor Blue
python --version

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Blue
pip install -e ".[dev]"

# Check executable
Write-Host "🔍 Checking executable..." -ForegroundColor Blue
try {
    Get-Command lazydjango -ErrorAction Stop
    Write-Host "✓ lazydjango executable found" -ForegroundColor Green
    lazydjango --help | Out-Null
    Write-Host "✓ lazydjango runs successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ lazydjango executable not found" -ForegroundColor Red
    exit 1
}

# Run linting
Write-Host "🎨 Running linting..." -ForegroundColor Blue
ruff check lazydjango/
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Ruff found issues" -ForegroundColor Yellow
}

black --check lazydjango/
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Black formatting needed" -ForegroundColor Yellow
}

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Blue
pytest --cov=lazydjango --cov-report=term

# Security checks
Write-Host "🔒 Running security checks..." -ForegroundColor Blue
bandit -r lazydjango/
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Bandit found issues" -ForegroundColor Yellow
}

safety check
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Safety found vulnerabilities" -ForegroundColor Yellow
}

# Build check
Write-Host "📦 Building package..." -ForegroundColor Blue
python -m build

Write-Host "✅ All checks completed!" -ForegroundColor Green
