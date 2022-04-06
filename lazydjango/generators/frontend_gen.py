"""Frontend generator."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class FrontendGenerator:
    """Generates Django forms and HTML templates."""

    def __init__(
        self,
        app_name: str,
        model_name: str,
        gen_type: str = "both",
        style: str = "bootstrap",
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.app_name = app_name
        self.model_name = model_name
        self.gen_type = gen_type
        self.style = style
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Generate forms and templates."""
        try:
            template_dir = Path(__file__).parent.parent / "templates"
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(),
            )

            if self.gen_type in ("form", "both"):
                form_template = env.get_template("forms.py.j2")
                form_code = form_template.render(
                    model_name=self.model_name,
                    model_name_lower=self.model_name.lower(),
                )

                if not self.dry_run:
                    forms_file = self.project_path / self.app_name / "forms.py"
                    if forms_file.exists():
                        existing_content = forms_file.read_text()
                        if f"class {self.model_name}Form" in existing_content:
                            print(
                                f"Warning: Form for '{self.model_name}' already exists. Skipping..."
                            )
                        else:
                            with open(forms_file, "a") as f:
                                f.write("\n\n")
                                f.write(form_code)
                    else:
                        with open(forms_file, "w") as f:
                            f.write(form_code)

            if self.gen_type in ("template", "both"):
                html_template = env.get_template("html-form.html.j2")
                html_code = html_template.render(
                    model_name=self.model_name,
                    model_name_lower=self.model_name.lower(),
                    style=self.style,
                )

                if not self.dry_run:
                    templates_dir = self.project_path / self.app_name / "templates" / self.app_name
                    templates_dir.mkdir(parents=True, exist_ok=True)

                    html_file = templates_dir / f"{self.model_name.lower()}_form.html"
                    if html_file.exists():
                        print(
                            f"Warning: Template for '{self.model_name}' already exists. Skipping..."
                        )
                    else:
                        with open(html_file, "w") as f:
                            f.write(html_code)

            return True
        except Exception as e:
            print(f"Error generating frontend: {e}")
            return False
