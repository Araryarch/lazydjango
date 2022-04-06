"""Model generator."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from lazydjango.api.models import FieldDefinition


class ModelGenerator:
    """Generates Django model code."""

    def __init__(
        self,
        app_name: str,
        model_name: str,
        fields: list[FieldDefinition],
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.app_name = app_name
        self.model_name = model_name
        self.fields = fields
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Generate the model."""
        try:
            template_dir = Path(__file__).parent.parent / "templates"
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(),
            )
            template = env.get_template("model.py.j2")

            model_code = template.render(
                model_name=self.model_name,
                fields=self.fields,
            )

            models_file = self.project_path / self.app_name / "models.py"

            if not self.dry_run:
                if models_file.exists():
                    existing_content = models_file.read_text()
                    if f"class {self.model_name}" in existing_content:
                        print(f"Warning: Model '{self.model_name}' already exists. Skipping...")
                        return True

                    with open(models_file, "a") as f:
                        f.write("\n\n")
                        f.write(model_code)
                else:
                    with open(models_file, "w") as f:
                        f.write("from django.db import models\n\n\n")
                        f.write(model_code)

                self._register_app()
                self._run_migrations()

            return True
        except Exception as e:
            print(f"Error generating model: {e}")
            return False

    def _register_app(self) -> None:
        """Register app in settings if not already registered."""
        settings_file = self.project_path / "settings.py"
        if not settings_file.exists():
            return

        content = settings_file.read_text()
        app_config = f"'{self.app_name}'"

        if app_config not in content:
            content = content.replace(
                "INSTALLED_APPS = [",
                f"INSTALLED_APPS = [\n    '{self.app_name}',",
            )
            settings_file.write_text(content)

        self._ensure_wsgi_file()

    def _ensure_wsgi_file(self) -> None:
        """Ensure wsgi.py exists."""
        wsgi_file = self.project_path / "wsgi.py"
        if wsgi_file.exists():
            return

        wsgi_content = """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()
"""
        wsgi_file.write_text(wsgi_content)

    def _run_migrations(self) -> None:
        """Run Django migrations."""
        import subprocess

        try:
            subprocess.run(
                ["python", "manage.py", "makemigrations", self.app_name],
                cwd=self.project_path,
                check=True,
            )
            subprocess.run(
                ["python", "manage.py", "migrate"],
                cwd=self.project_path,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Migration error: {e}")
