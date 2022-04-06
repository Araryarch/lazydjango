"""View generator."""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ViewGenerator:
    """Generates Django view code."""

    def __init__(
        self,
        app_name: str,
        model_name: str,
        view_type: str = "template",
        operations: dict | None = None,
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.app_name = app_name
        self.model_name = model_name
        self.model_name_lower = model_name.lower()
        self.view_type = view_type
        self.operations = operations or {
            "list": True,
            "create": True,
            "detail": True,
            "update": True,
            "delete": True,
        }
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Generate views."""
        try:
            template_dir = Path(__file__).parent.parent / "templates"
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(),
            )

            template = env.get_template("view.py.j2")

            fields = self._get_model_fields()

            view_code = template.render(
                app_name=self.app_name,
                model_name=self.model_name,
                model_name_lower=self.model_name.lower(),
                operations=self.operations,
                fields=fields,
            )

            if not self.dry_run:
                views_file = self.project_path / self.app_name / "views.py"

                if views_file.exists():
                    existing_content = views_file.read_text()

                    new_functions = self._get_new_functions(view_code)

                    missing_functions = [
                        fn for fn in new_functions if f"def {fn}(" not in existing_content
                    ]

                    if missing_functions:
                        if not self._has_required_imports(existing_content, self.model_name):
                            imports = self._get_imports_string(self.model_name)
                            existing_content = imports + "\n\n" + existing_content

                        stripped = self._strip_imports(view_code)
                        existing_content += "\n\n" + stripped
                        views_file.write_text(existing_content)
                        print(f"Added views: {missing_functions}")
                    else:
                        print(f"All requested views for '{self.model_name}' already exist.")
                else:
                    full_code = self._add_imports_to_code(view_code, self.model_name)
                    views_file.write_text(full_code)

                self._update_urls()

            return True
        except Exception as e:
            print(f"Error generating views: {e}")
            return False

    def _get_model_fields(self):
        """Get model fields for view rendering."""
        try:
            model_file = self.project_path / self.app_name / "models.py"
            if model_file.exists():
                content = model_file.read_text()
                import ast

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == self.model_name:
                        fields = []
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        field_type = "CharField"
                                        if hasattr(item, "value") and hasattr(item.value, "func"):
                                            if hasattr(item.value.func, "attr"):
                                                field_type = item.value.func.attr
                                            elif hasattr(item.value.func, "id"):
                                                field_type = item.value.func.id
                                        fields.append({"name": target.id, "field_type": field_type})
                        return fields
        except Exception:
            pass
        return [{"name": "id", "field_type": "IntegerField"}]

    def _update_urls(self) -> None:
        """Update URL configuration."""
        try:
            urls_file = self.project_path / self.app_name / "urls.py"

            template_dir = Path(__file__).parent.parent / "templates"
            env_url = Environment(loader=FileSystemLoader(template_dir))
            template = env_url.get_template("urls.py.j2")

            url_pattern = template.render(
                app_name=self.app_name,
                model_name=self.model_name,
                model_name_lower=self.model_name.lower(),
                view_type=self.view_type,
                operations=self.operations,
            )

            if urls_file.exists():
                existing_content = urls_file.read_text()

                new_paths = re.findall(r"path\s*\(\s*['\"]([^'\"]+)['\"]", url_pattern)
                existing_paths = re.findall(r"path\s*\(\s*['\"]([^'\"]+)['\"]", existing_content)

                missing_paths = [p for p in new_paths if p not in existing_paths]

                if not missing_paths:
                    print(f"All URLs for '{self.model_name}' already exist. Skipping...")
                    return

                lines = existing_content.split("\n")
                insert_idx = None
                for i, line in enumerate(lines):
                    if line.strip().startswith("]") and i > 0:
                        insert_idx = i
                        break

                new_url_lines = []
                for path_str in missing_paths:
                    for url_line in url_pattern.strip().split("\n"):
                        if f"'{path_str}'" in url_line or f'"{path_str}"' in url_line:
                            stripped = url_line.strip()
                            if stripped:
                                new_url_lines.append("    " + stripped)
                            break

                if insert_idx:
                    lines = lines[:insert_idx] + new_url_lines + lines[insert_idx:]
                else:
                    lines.extend(new_url_lines)

                result = "\n".join(lines)

                if "from django.urls import path" not in result:
                    if "from . import views" in result:
                        result = result.replace(
                            "from . import views",
                            "from django.urls import path\nfrom . import views",
                        )
                    else:
                        result = "from django.urls import path\nfrom . import views\n\n" + result

                urls_file.write_text(result)
            else:
                with open(urls_file, "w") as f:
                    f.write("from django.urls import path\n")
                    f.write("from . import views\n\n")
                    f.write("urlpatterns = [\n")
                    f.write(url_pattern)
                    f.write("]\n")

        except Exception as e:
            print(f"Error updating urls: {e}")

    def _strip_imports(self, code: str) -> str:
        """Strip import statements from code."""
        lines = code.split("\n")
        result_lines = []
        skip_until_blank = False
        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("from django")
                or stripped.startswith("from .models")
                or stripped.startswith("import json")
            ):
                skip_until_blank = True
                continue
            if skip_until_blank:
                if not stripped:
                    skip_until_blank = False
                continue
            result_lines.append(line)
        return "\n".join(result_lines).strip()

    def _get_new_functions(self, code: str) -> list[str]:
        """Get list of function names from code."""
        pattern = r"def\s+(\w+)\s*\("
        return re.findall(pattern, code)

    def _get_imports_string(self, model_name: str) -> str:
        """Get the imports string for a model."""
        return f"""from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import {model_name}
import json"""

    def _has_required_imports(self, code: str, model_name: str) -> bool:
        """Check if code has required imports."""
        required = [
            "from django.views.decorators.csrf import csrf_exempt",
            f"from .models import {model_name}",
        ]
        return all(imp in code for imp in required)

    def _add_imports_to_code(self, code: str, model_name: str) -> str:
        """Add imports to code if not present."""
        imports = self._get_imports_string(model_name)
        stripped = self._strip_imports(code)
        return imports + "\n\n" + stripped
