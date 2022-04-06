#!/usr/bin/env python3
"""Build script for lazydjango package."""

import os
import shutil
import subprocess
import sys
import platform
from pathlib import Path


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def is_windows():
    return platform.system() == "Windows"


def run_command(cmd: list, cwd: str = ".", capture: bool = True):
    """Run a command and return success status."""
    print(f"  Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=capture,
            text=True,
            timeout=600,
        )
        if result.stdout:
            for line in result.stdout.splitlines()[-20:]:
                print(f"    {line}")
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 10 minutes"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or str(e)
        for line in error_msg.splitlines()[-10:]:
            print(f"    {Colors.RED}{line}{Colors.RESET}")
        return False, error_msg
    except FileNotFoundError as e:
        missing = str(e).strip("[]'")
        return False, f"Command not found: {missing}"


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def check_node():
    """Check if Node.js is installed."""
    if not check_command_exists("node"):
        print(f"{Colors.YELLOW}Warning: Node.js not found. UI build will be skipped.{Colors.RESET}")
        print(f"{Colors.YELLOW}Install Node.js from https://nodejs.org/{Colors.RESET}")
        return False
    return True


def check_npm():
    """Check if npm is installed."""
    if not check_command_exists("npm"):
        print(f"{Colors.YELLOW}Warning: npm not found. UI build will be skipped.{Colors.RESET}")
        return False
    return True


def build_ui():
    """Build the Next.js UI for static export."""
    ui_path = Path("ui")
    if not ui_path.exists():
        print(f"{Colors.YELLOW}UI folder not found, skipping...{Colors.RESET}")
        return True

    if not check_node() or not check_npm():
        print(f"{Colors.YELLOW}Skipping UI build due to missing dependencies{Colors.RESET}")
        return True

    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BLUE}Building UI...{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}\n")

    print("Installing UI dependencies...")
    success, _ = run_command(["npm", "install"], cwd="ui")
    if not success:
        print(
            f"{Colors.YELLOW}Warning: npm install failed, using existing node_modules{Colors.RESET}"
        )

    print("\nBuilding UI...")
    success, output = run_command(["npm", "run", "build"], cwd="ui")
    if not success:
        print(f"{Colors.YELLOW}Warning: UI build failed, continuing without UI{Colors.RESET}")
        return True

    out_dir = ui_path / "out"
    if out_dir.exists():
        next_dir = out_dir / "_next"
        pkg_ui_out = Path("lazydjango/ui/out")

        if pkg_ui_out.exists():
            shutil.rmtree(pkg_ui_out)

        pkg_ui_out.mkdir(parents=True, exist_ok=True)

        for item in out_dir.iterdir():
            if item.name.startswith("."):
                continue
            dest = pkg_ui_out / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        print(f"{Colors.GREEN}[OK] UI built and copied to package{Colors.RESET}")
    else:
        print(
            f"{Colors.YELLOW}Warning: UI build completed but output folder not found{Colors.RESET}"
        )

    return True


def clean_build_dirs():
    """Clean previous build artifacts."""
    dirs_to_clean = ["dist", "build", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Cleaning: {path}")
                shutil.rmtree(path)


def build_package():
    """Build the Python package."""
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BLUE}Building Python package...{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}\n")

    clean_build_dirs()

    success, output = run_command([sys.executable, "-m", "build"])
    if not success:
        print(f"{Colors.RED}Failed to build package:{Colors.RESET}")
        return False

    dist_path = Path("dist")
    if dist_path.exists():
        files = list(dist_path.glob("*"))
        print(f"\n{Colors.GREEN}[OK] Package built successfully!{Colors.RESET}")
        print(f"\nFiles in dist/:")
        for f in files:
            size = f.stat().st_size
            size_str = (
                f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
            )
            print(f"  {Colors.GREEN}{f.name}{Colors.RESET} ({size_str})")
    else:
        print(f"{Colors.YELLOW}Warning: dist folder not found{Colors.RESET}")

    return True


def verify_package():
    """Verify the built package."""
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BLUE}Verifying package...{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}\n")

    try:
        import twine
    except ImportError:
        print(f"{Colors.YELLOW}Installing twine for verification...{Colors.RESET}")
        success, _ = run_command([sys.executable, "-m", "pip", "install", "twine"])
        if not success:
            print(f"{Colors.YELLOW}Skipping package verification{Colors.RESET}")
            return True

    success, output = run_command(["twine", "check", "dist/*"])
    if not success:
        print(f"{Colors.YELLOW}Package check warning (may be informational):{Colors.RESET}")

    return True


def main():
    """Main build function."""
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  LazyDjango Build Script{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")
    print()
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version.split()[0]}")
    print()

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python build_script.py [options]")
        print()
        print("Options:")
        print("  --ui-only       Build only the UI")
        print("  --package-only  Build only the Python package (skip UI)")
        print("  --verify        Verify the built package with twine")
        print("  --clean         Clean build artifacts first")
        print("  --help, -h      Show this help message")
        return 0

    if "--package-only" in sys.argv:
        success = build_package()
        return 0 if success else 1

    if "--ui-only" in sys.argv:
        success = build_ui()
        return 0 if success else 1

    if "--clean" in sys.argv:
        clean_build_dirs()
        print()

    ui_success = build_ui()

    pkg_success = build_package()
    if not pkg_success:
        print(f"\n{Colors.RED}Package build failed!{Colors.RESET}")
        return 1

    if "--verify" in sys.argv:
        verify_package()

    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}  Build Complete!{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 50}{Colors.RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
