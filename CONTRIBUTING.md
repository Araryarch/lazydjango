# Contributing to LazyDjango

Terima kasih atas minat Anda untuk berkontribusi pada LazyDjango!

## Development Setup

1. Clone repository:
```bash
git clone https://github.com/Araryarch/lazydjango.git
cd lazydjango
```

2. Buat virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

### Local Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lazydjango --cov-report=html

# Run specific test file
pytest tests/test_cli.py
```

### Cross-Platform Testing

Project ini menggunakan GitHub Actions untuk testing otomatis di:
- Ubuntu (Linux)
- Windows
- macOS

Setiap push atau pull request akan otomatis menjalankan:
1. Unit tests di semua platform
2. Security checks (bandit, safety)
3. Executable safety checks
4. Build & package verification

## Code Quality

### Linting
```bash
# Check code style
ruff check lazydjango/
black --check lazydjango/

# Auto-fix issues
ruff check --fix lazydjango/
black lazydjango/
```

### Security Checks
```bash
# Check for vulnerabilities
safety check
bandit -r lazydjango/
```

## Testing Executable

### Linux/Mac
```bash
# Test executable exists
which lazydjango
command -v lazydjango

# Test it runs
lazydjango --help
```

### Windows
```powershell
# Test executable exists
Get-Command lazydjango

# Test it runs
lazydjango --help
```

## Pull Request Process

1. Fork repository
2. Buat branch baru (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buka Pull Request

### PR Checklist
- [ ] Tests pass di semua platform
- [ ] Code mengikuti style guide (ruff, black)
- [ ] Security checks pass
- [ ] Documentation updated (jika perlu)
- [ ] Executable berfungsi di Windows, Linux, dan macOS

## Reporting Issues

Saat melaporkan bug, sertakan:
- OS dan versi (Windows 11, Ubuntu 22.04, macOS 13, dll)
- Python version
- Error message lengkap
- Steps to reproduce

## Questions?

Jangan ragu untuk membuka issue untuk pertanyaan atau diskusi!
