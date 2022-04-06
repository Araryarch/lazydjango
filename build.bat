@echo off
REM LazyDjango Build Script for Windows

echo ======================================
echo   LazyDjango Build Script
echo ======================================

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info

REM Build UI if Node.js is available
where node >nul 2>nul
if %errorlevel%==0 (
    echo.
    echo Building Next.js UI...
    cd ui
    call npm install
    call npm run build
    cd ..
    
    REM Copy UI to package
    if exist ui\out (
        if exist lazydjango\ui\out rmdir /s /q lazydjango\ui\out
        xcopy /s /e /i ui\out lazydjango\ui\out
        echo UI copied to lazydjango\ui\out
    )
) else (
    echo Node.js not found, skipping UI build...
)

REM Build Python package
echo.
echo Building Python package...
python -m pip install --upgrade pip build twine
python -m build

echo.
echo Build complete! Files in dist/

REM List files
dir dist\

echo.
echo ======================================
echo   Build Complete!
echo ======================================
echo.
echo To upload to TestPyPI:
echo   python -m twine upload --repository testpypi dist/*
echo.
echo To upload to PyPI:
echo   python -m twine upload dist/*
