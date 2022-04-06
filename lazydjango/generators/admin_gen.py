"""Admin generator."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class AdminGenerator:
    """Generates Django admin configuration."""

    def __init__(
        self,
        app_name: str,
        model_name: str,
        options: dict,
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.app_name = app_name
        self.model_name = model_name
        self.options = options
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Generate admin configuration."""
        try:
            template_dir = Path(__file__).parent.parent / "templates"
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(),
            )
            template = env.get_template("admin.py.j2")

            fields = self._get_model_fields()

            admin_code = template.render(
                model_name=self.model_name,
                options=self.options,
                fields=fields,
            )

            if not self.dry_run:
                admin_file = self.project_path / self.app_name / "admin.py"

                if admin_file.exists():
                    existing_content = admin_file.read_text()
                    if (
                        f"@admin.register({self.model_name})" in existing_content
                        or f"admin.site.register({self.model_name})" in existing_content
                    ):
                        print(f"Warning: Admin for '{self.model_name}' already exists. Skipping...")
                        return True

                    with open(admin_file, "a") as f:
                        f.write("\n\n")
                        f.write(admin_code)
                else:
                    with open(admin_file, "w") as f:
                        f.write("from django.contrib import admin\n")
                        f.write(f"from .models import {self.model_name}\n\n\n")
                        f.write(admin_code)

                self._setup_admin_theme()

            return True
        except Exception as e:
            print(f"Error generating admin: {e}")
            return False

    def _setup_admin_theme(self) -> None:
        """Setup admin theme if selected."""
        theme = self.options.get("admin_theme", "none")
        if theme == "none":
            return

        theme_info = {
            "unfold": {
                "package": "django-unfold",
                "pip": "django-unfold",
                "setting": "X_FRAME_OPTIONS = 'sameorigin'\n\nINSTALLED_APPS += ['unfold']\n\n",
            },
            "jet": {
                "package": "django-jet",
                "pip": "django-jet",
                "setting": "INSTALLED_APPS += ['jet', 'jet.dashboard']\n",
            },
            "adminlte": {
                "package": "django-adminlte3",
                "pip": "django-adminlte3",
                "setting": "INSTALLED_APPS += ['adminlte3']\n",
            },
            "tabler": {
                "package": "django-tabler",
                "pip": "django-tabler",
                "setting": "INSTALLED_APPS += ['tabler']\n",
            },
        }

        info = theme_info.get(theme)
        if not info:
            return

        print(f"Theme '{theme}' selected. To install, run:")
        print(f"  pip install {info['pip']}")

    def _get_model_fields(self) -> list:
        """Extract field names from model."""
        import ast

        fields = []
        model_file = self.project_path / self.app_name / "models.py"
        if model_file.exists():
            try:
                tree = ast.parse(model_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == self.model_name:
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        fields.append(target.id)
            except Exception:
                pass
        return fields
