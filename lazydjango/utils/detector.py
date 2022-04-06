"""Django project detector utility."""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelInfo:
    """Represents a detected model."""

    name: str
    fields: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)


@dataclass
class RouteInfo:
    """Represents a detected route."""

    path: str
    view_name: str
    model_name: str = ""


@dataclass
class AppInfo:
    """Represents a detected app with its models and routes."""

    name: str
    models: list[ModelInfo] = field(default_factory=list)
    routes: list[RouteInfo] = field(default_factory=list)


@dataclass
class DjangoProject:
    """Represents a detected Django project."""

    root: Path
    settings_path: Path
    manage_path: Path
    project_name: str
    apps: list[str]
    app_details: dict[str, AppInfo] = field(default_factory=dict)


class DjangoProjectDetector:
    """Detects Django project structure."""

    def __init__(self, path: Path = Path(".")):
        self.path = path.resolve()
        self.project: DjangoProject | None = None
        self.is_django_project = False
        self.last_error: str | None = None

    def detect(self) -> bool:
        """Detect Django project at given path."""
        self.project = None
        self.is_django_project = False
        self.last_error = None

        if not self.path.exists():
            self.last_error = f"Path does not exist: {self.path}"
            return False

        if not self.path.is_dir():
            self.last_error = f"Path is not a directory: {self.path}"
            return False

        settings_py = self.path / "settings.py"
        manage_py = self.path / "manage.py"

        if settings_py.exists() and manage_py.exists():
            project_name = self.path.name
            apps = self._detect_apps(self.path)
            self.project = DjangoProject(
                root=self.path,
                settings_path=settings_py,
                manage_path=manage_py,
                project_name=project_name,
                apps=apps,
            )
            self.is_django_project = True
            return True

        for item in self.path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                settings_file = item / "settings.py"
                manage_file = item / "manage.py"
                if settings_file.exists() and manage_file.exists():
                    project_name = item.name
                    apps = self._detect_apps(item)
                    self.project = DjangoProject(
                        root=item,
                        settings_path=settings_file,
                        manage_path=manage_file,
                        project_name=project_name,
                        apps=apps,
                    )
                    self.is_django_project = True
                    return True

        for item in self.path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                settings_file = item / "settings.py"
                manage_file = self.path / "manage.py"
                if settings_file.exists() and manage_file.exists():
                    project_name = item.name
                    apps = self._detect_apps(self.path)
                    self.project = DjangoProject(
                        root=self.path,
                        settings_path=settings_file,
                        manage_path=manage_file,
                        project_name=project_name,
                        apps=apps,
                    )
                    self.is_django_project = True
                    return True

        return False

    def _detect_apps(self, project_root: Path) -> list[str]:
        """Detect Django apps in project."""
        apps = []
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith(".") and (item / "apps.py").exists():
                try:
                    with open(item / "apps.py") as f:
                        content = f.read()
                        if "AppConfig" in content:
                            apps.append(item.name)
                except Exception:
                    pass
        return sorted(apps)

    def _detect_models_in_app(self, app_name: str) -> list[ModelInfo]:
        """Detect models in an app."""
        if not self.project:
            return []

        models = []
        models_file = self.project.root / app_name / "models.py"

        if not models_file.exists():
            return []

        try:
            content = models_file.read_text()

            class_matches = list(re.finditer(r"class\s+(\w+)\s*\(\s*models\.Model\s*\):", content))

            for i, class_match in enumerate(class_matches):
                model_name = class_match.group(1)
                class_start = class_match.start()
                class_end = (
                    class_matches[i + 1].start() if i + 1 < len(class_matches) else len(content)
                )

                class_body = content[class_start:class_end]

                fields = []
                relationships = []

                field_patterns = re.finditer(
                    r"^\s{4}(\w+)\s*=\s*models\.(\w+)\s*\(", class_body, re.MULTILINE
                )

                for field_match in field_patterns:
                    field_name = field_match.group(1)
                    field_type = field_match.group(2)

                    if field_name in ("class", "Meta", "objects", "pk"):
                        continue

                    field_start = field_match.end()
                    paren_count = 1
                    field_end = field_start
                    for j in range(field_start, min(field_start + 500, len(class_body))):
                        if class_body[j] == "(":
                            paren_count += 1
                        elif class_body[j] == ")":
                            paren_count -= 1
                            if paren_count == 0:
                                field_end = j + 1
                                break

                    field_params = class_body[field_start:field_end].strip()

                    if field_type in ("ForeignKey", "OneToOneField"):
                        to_model = "Unknown"

                        match = re.search(r"['\"](\w+(?:\.\w+)?)['\"]", field_params)
                        if match:
                            to_model = match.group(1)
                        else:
                            match = re.match(r"(\w+)", field_params)
                            if match:
                                to_model = match.group(1)

                        if "." in to_model:
                            to_model = to_model.split(".")[-1]
                        rel_type = "ManyToOne" if field_type == "ForeignKey" else "OneToOne"
                        relationships.append(
                            {"name": field_name, "type": rel_type, "to_model": to_model}
                        )
                        fields.append({"name": field_name, "type": field_type, "to": to_model})
                    elif field_type == "ManyToManyField":
                        to_model = "Unknown"

                        match = re.search(r"['\"](\w+(?:\.\w+)?)['\"]", field_params)
                        if match:
                            to_model = match.group(1)
                        else:
                            match = re.match(r"(\w+)", field_params)
                            if match:
                                to_model = match.group(1)

                        if "." in to_model:
                            to_model = to_model.split(".")[-1]
                        relationships.append(
                            {"name": field_name, "type": "ManyToMany", "to_model": to_model}
                        )
                        fields.append({"name": field_name, "type": field_type, "to": to_model})
                    else:
                        fields.append({"name": field_name, "type": field_type})

                models.append(
                    ModelInfo(name=model_name, fields=fields, relationships=relationships)
                )
        except Exception as e:
            import sys

            print(f"Error detecting models in app '{app_name}': {e}", file=sys.stderr)

        return models

    def _detect_routes_in_app(self, app_name: str) -> list[RouteInfo]:
        """Detect routes in an app."""
        if not self.project:
            return []

        routes = []
        urls_file = self.project.root / app_name / "urls.py"

        if not urls_file.exists():
            return []

        try:
            content = urls_file.read_text()

            route_patterns = re.findall(
                r"path\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*views\.(\w+)\s*", content
            )

            for path_str, view_name in route_patterns:
                model_name = self._extract_model_from_view_name(view_name)
                routes.append(RouteInfo(path=path_str, view_name=view_name, model_name=model_name))
        except Exception:
            pass

        return routes

    def _extract_model_from_view_name(self, view_name: str) -> str:
        """Extract model name from view function name."""
        suffixes = ["_list", "_create", "_detail", "_update", "_delete", "_list"]
        for suffix in suffixes:
            if view_name.endswith(suffix):
                return view_name.replace(suffix, "").title()
        return view_name

    def detect_full(self) -> bool:
        """Detect Django project with full details including models and routes."""
        if not self.detect():
            return False

        if self.project:
            for app_name in self.project.apps:
                models = self._detect_models_in_app(app_name)
                routes = self._detect_routes_in_app(app_name)
                self.project.app_details[app_name] = AppInfo(
                    name=app_name, models=models, routes=routes
                )

        return True

    def get_manage_py_path(self) -> Path | None:
        """Get path to manage.py"""
        if self.project:
            return self.project.manage_path
        return None

    def get_settings_path(self) -> Path | None:
        """Get path to settings.py"""
        if self.project:
            return self.project.settings_path
        return None

    def get_project_root(self) -> Path | None:
        """Get project root path"""
        if self.project:
            return self.project.root
        return None

    def get_existing_models(self, app_name: str) -> list[str]:
        """Get existing model names in an app for relationship selection."""
        if not self.project:
            return []

        models = []
        app_path = self.project.root / app_name / "models.py"

        if not app_path.exists():
            return []

        try:
            with open(app_path) as f:
                content = f.read()
                import re

                model_matches = re.findall(r"class\s+(\w+)\s*\(", content)
                models = model_matches
        except Exception:
            pass

        return models
