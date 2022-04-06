"""Static generator - TailwindCSS and Bootstrap setup."""

import subprocess
from pathlib import Path


class StaticGenerator:
    """Generates static file configuration for TailwindCSS and Bootstrap."""

    def __init__(
        self,
        framework: str = "tailwind",
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.framework = framework
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Setup static files."""
        try:
            if self.framework == "tailwind":
                return self._setup_tailwind()
            elif self.framework == "bootstrap":
                return self._setup_bootstrap()
            return False
        except Exception as e:
            print(f"Error setting up static: {e}")
            return False

    def _setup_tailwind(self) -> bool:
        """Setup TailwindCSS using npm."""
        if self.dry_run:
            print("DRY RUN: Would setup TailwindCSS via npm")
            return True

        try:
            import subprocess

            settings_file = self.project_path / "settings.py"
            if settings_file.exists():
                content = settings_file.read_text()

                if "django_tailwind_cli" not in content:
                    content = content.replace(
                        "INSTALLED_APPS = [",
                        "INSTALLED_APPS = [\n    'django_tailwind_cli',",
                    )
                    settings_file.write_text(content)

            static_dir = self.project_path / "static" / "css"
            static_dir.mkdir(parents=True, exist_ok=True)

            css_file = static_dir / "styles.css"
            if not css_file.exists():
                css_file.write_text('@import "tailwindcss";\n')

            tailwind_config = self.project_path / "tailwind.config.js"
            if not tailwind_config.exists():
                tailwind_config.write_text("""/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""")

            package_json = self.project_path / "package.json"
            if not package_json.exists():
                package_json.write_text(
                    '{"name": "myproject", "scripts": {"build": "tailwindcss -i ./static/css/styles.css -o ./static/css/output.css"}}\n'
                )

            subprocess.run(
                ["npm", "install", "-D", "tailwindcss", "postcss", "autoprefixer"],
                cwd=self.project_path,
                capture_output=True,
            )

            subprocess.run(
                ["npx", "tailwindcss", "init"],
                cwd=self.project_path,
                capture_output=True,
            )

            print("TailwindCSS setup completed!")
            print("Run 'npm run build' to compile CSS")
            return True

        except Exception as e:
            print(f"TailwindCSS setup error: {e}")
            return False

    def _setup_bootstrap(self) -> bool:
        """Setup Bootstrap 5 static files using npm."""
        if self.dry_run:
            print("DRY RUN: Would setup Bootstrap 5 via npm")
            return True

        try:
            static_dir = self.project_path / "static"
            bootstrap_dir = static_dir / "bootstrap"
            bootstrap_css = bootstrap_dir / "css"
            bootstrap_js = bootstrap_dir / "js"

            bootstrap_css.mkdir(parents=True, exist_ok=True)
            bootstrap_js.mkdir(parents=True, exist_ok=True)

            subprocess.run(
                ["npm", "install", "bootstrap@5"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            node_modules = self.project_path / "node_modules" / "bootstrap"
            if node_modules.exists():
                import shutil

                src_css = node_modules / "dist" / "css"
                src_js = node_modules / "dist" / "js"

                if src_css.exists():
                    for f in src_css.glob("*.min.css"):
                        shutil.copy(f, bootstrap_css)
                if src_js.exists():
                    for f in src_js.glob("*.min.js"):
                        shutil.copy(f, bootstrap_js)
            else:
                import urllib.request

                css_url = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
                js_url = (
                    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
                )

                css_file = bootstrap_css / "bootstrap.min.css"
                js_file = bootstrap_js / "bootstrap.bundle.min.js"

                urllib.request.urlretrieve(css_url, css_file)
                urllib.request.urlretrieve(js_url, js_file)

            base_template = self.project_path / "templates" / "base.html"
            base_template.parent.mkdir(parents=True, exist_ok=True)

            if not base_template.exists():
                base_template.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Django App{% endblock %}</title>
    <link href="{% static 'bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    <script src="{% static 'bootstrap/js/bootstrap.bundle.min.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
""")

            print("Bootstrap 5 setup completed!")
            return True

        except Exception as e:
            print(f"Bootstrap setup error: {e}")
            return False
