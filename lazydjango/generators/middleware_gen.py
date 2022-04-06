"""Middleware generator."""

from pathlib import Path


class MiddlewareGenerator:
    """Generates Django middleware."""

    def __init__(
        self,
        middleware_name: str,
        middleware_type: str = "logging",
        custom_code: str = "",
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.middleware_name = middleware_name
        self.middleware_type = middleware_type
        self.custom_code = custom_code
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Generate middleware."""
        try:
            if not self.dry_run:
                self._save_middleware()
                self._update_settings()

            return True
        except Exception as e:
            print(f"Error generating middleware: {e}")
            return False

    def _generate_code(self) -> str:
        """Generate middleware code."""
        class_name = (
            self.middleware_name
            if self.middleware_name.endswith("Middleware")
            else f"{self.middleware_name}Middleware"
        )
        return f"""
import logging
import time

logger = logging.getLogger(__name__)


class {class_name}:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        logger.info(f"Request: {{request.method}} {{request.path}}")

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(f"Response: {{response.status_code}} - Duration: {{duration:.3f}}s")

        return response
"""

    def _save_middleware(self) -> None:
        """Save middleware to project myproject folder."""
        project_name = self._detect_project_name()
        middleware_dir = self.project_path / project_name
        middleware_dir.mkdir(parents=True, exist_ok=True)

        middleware_file = middleware_dir / "middleware.py"
        code = self._generate_code()
        class_name = (
            self.middleware_name
            if self.middleware_name.endswith("Middleware")
            else f"{self.middleware_name}Middleware"
        )

        if middleware_file.exists():
            with open(middleware_file) as f:
                existing = f.read()
            if f"class {class_name}" in existing:
                return
            with open(middleware_file, "a") as f:
                f.write(code)
        else:
            with open(middleware_file, "w") as f:
                f.write(code)

    def _detect_project_name(self) -> str:
        """Detect Django project name."""
        if (self.project_path / "manage.py").exists():
            with open(self.project_path / "manage.py") as f:
                content = f.read()
                if "myproject" in content:
                    return "myproject"
                import re

                match = re.search(
                    r'os\.environ\.get\([\'"]DJANGO_SETTINGS_MODULE[\'"]\)\s*or\s*[\'"](\w+)\.',
                    content,
                )
                if match:
                    return match.group(1)
        return "myproject"

    def _update_settings(self) -> None:
        """Update Django settings."""
        project_name = self._detect_project_name()
        settings_file = self.project_path / project_name / "settings.py"

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        class_name = (
            self.middleware_name
            if self.middleware_name.endswith("Middleware")
            else f"{self.middleware_name}Middleware"
        )
        middleware_path = f"{project_name}.middleware.{class_name}"

        if middleware_path not in content:
            content = content.replace("MIDDLEWARE = [", f"MIDDLEWARE = [\n    '{middleware_path}',")
            settings_file.write_text(content)
