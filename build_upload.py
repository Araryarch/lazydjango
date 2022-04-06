#!/usr/bin/env python3
"""Build and upload script for lazydjango."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str = ".") -> tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode, result.stdout, result.stderr


def clean():
    """Clean build directories."""
    dirs = ["dist", "build", "*.egg-info"]
    for d in dirs:
        for path in Path(".").glob(d):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)


def build_ui():
    """Build Next.js UI."""
    if not Path("ui").exists():
        print("UI folder not found, skipping...")
        return True

    if not shutil.which("node") and not shutil.which("node.exe"):
        print("Node.js not found, skipping UI build...")
        return True

    print("\n=== Building Next.js UI ===")

    run("npm install", cwd="ui")
    run("npm run build", cwd="ui")

    ui_out = Path("ui/out")
    pkg_ui_out = Path("lazydjango/ui/out")

    if ui_out.exists():
        if pkg_ui_out.exists():
            shutil.rmtree(pkg_ui_out)
        shutil.copytree(ui_out, pkg_ui_out)
        print(f"UI copied to {pkg_ui_out}")

    return True


def build():
    """Build Python package."""
    print("\n=== Building Python Package ===")

    clean()

    code, _, _ = run("python -m pip install build twine --upgrade")
    code, _, _ = run("python -m build")

    dist = Path("dist")
    if dist.exists():
        files = list(dist.glob("*"))
        print(f"\n=== Built files ===")
        for f in files:
            size = f.stat().st_size
            size_str = (
                f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
            )
            print(f"  {f.name} ({size_str})")

    return True


def upload(repo: str = "testpypi"):
    """Upload to PyPI or TestPyPI."""
    print(f"\n=== Uploading to {repo} ===")

    dist = Path("dist")
    if not dist.exists() or not list(dist.glob("*.whl")):
        print("No wheel found. Run 'build' first.")
        return False

    code, _, _ = run(f"python -m twine upload --repository {repo} dist/*")

    if code == 0:
        print(f"\nSuccessfully uploaded to {repo}!")
    else:
        print(f"\nUpload failed!")

    return code == 0


def main():
    """Main entry point."""
    print("=" * 50)
    print("  LazyDjango Build & Upload Script")
    print("=" * 50)

    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nUsage:")
        print("  python build_upload.py          # Build only")
        print("  python build_upload.py build    # Build only")
        print("  python build_upload.py upload  # Upload to TestPyPI")
        print("  python build_upload.py upload pypi    # Upload to PyPI")
        print("  python build_upload.py all     # Build and upload to TestPyPI")
        print("  python build_upload.py clean   # Clean build directories")
        return 0

    if "--clean" in sys.argv or "clean" in sys.argv:
        clean()
        return 0

    if "build" in sys.argv or "all" in sys.argv or len(sys.argv) == 1:
        build_ui()
        if not build():
            return 1

    if "upload" in sys.argv:
        repo = "pypi" if "pypi" in sys.argv else "testpypi"
        upload(repo)

    return 0


if __name__ == "__main__":
    sys.exit(main())
