# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- GitHub Actions workflows untuk cross-platform testing (Windows, Linux, macOS)
- Executable safety checks di semua platform
- Security scanning dengan bandit dan safety
- Test suite dengan pytest dan coverage
- Local testing scripts untuk Windows (PowerShell) dan Unix (Bash)
- Comprehensive documentation untuk CI/CD workflows
- Contributing guidelines dengan testing instructions

### Changed
- Django Manager screen: Setiap section (Database, Development, Assets & Users, Info) sekarang punya border/kotak sendiri
- Django Manager screen: Server Status section sekarang punya border
- Django Manager screen: Output section sekarang punya border yang lebih jelas
- Django Manager screen: Info panel sekarang menampilkan Python version
- Improved visual hierarchy dengan background colors untuk panels

### Fixed
- 36 linting errors (unused imports, unused variables, f-string issues)
- Code formatting dengan black
- All ruff checks now pass

## [0.1.0] - Initial Release

### Features
- 📦 Model Generator - Create Django models with easy field selection
- 🎯 View Generator - Auto-generate CRUD views and URLs
- ⚙️ Admin Generator - Generate Django admin configuration
- 🎨 Frontend/Form Generator - Create Django forms and HTML templates
- 💅 TailwindCSS Setup - Auto configure TailwindCSS
- 💅 Bootstrap5 Setup - Auto configure Bootstrap 5 static files
- 🔐 JWT Auth Setup - Auto configure DRF + SimpleJWT
- 🔧 Middleware Generator - Generate custom middleware
- 🎮 Beautiful TUI interface with Textual
