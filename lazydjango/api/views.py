"""FastAPI views for lazydjango - Secure API for Django code generation."""

import json
import mimetypes
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response

from .models import (
    AdminCreateRequest,
    AppCreateRequest,
    AuthSetupRequest,
    FormCreateRequest,
    MiddlewareCreateRequest,
    ModelCreateRequest,
    ServerCommandRequest,
    StaticSetupRequest,
    ViewCreateRequest,
)

ALLOWED_COMMANDS = {"start", "migrate", "check", "shell"}
SAFE_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

app = FastAPI(
    title="LazyDjango API",
    description="Auto-generate Django code via REST API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def get_ui_path() -> Path | None:
    """Get the UI static files path."""
    import lazydjango

    package_dir = Path(lazydjango.__file__).parent

    ui_path = package_dir / "ui" / "out"
    if ui_path.exists():
        return ui_path

    ui_path = Path(__file__).parent.parent.parent / "ui" / "out"
    if ui_path.exists():
        return ui_path
    ui_path = Path(__file__).parent.parent / "ui" / "out"
    if ui_path.exists():
        return ui_path
    return None


def _find_project_dir(project_path: Path) -> Path | None:
    """Find the Django project directory (contains settings.py with INSTALLED_APPS)."""
    if (project_path / "settings.py").exists():
        return project_path
    for item in project_path.iterdir():
        if item.is_dir() and not item.name.startswith(".") and (item / "settings.py").exists():
            return item
    return None


def _update_settings_with_app(project_path: Path, app_name: str) -> None:
    """Update settings.py with new app."""
    proj_dir = _find_project_dir(project_path)
    if not proj_dir:
        return

    settings_file = proj_dir / "settings.py"
    if not settings_file.exists():
        return

    content = settings_file.read_text()

    if (
        f'"{app_name}"' not in content
        and f"'{app_name}'" not in content
        and "INSTALLED_APPS" in content
    ):
        content = content.replace("INSTALLED_APPS = [", f'INSTALLED_APPS = [\n    "{app_name}",')
        settings_file.write_text(content)


def _update_urls_with_app(project_path: Path, app_name: str) -> None:
    """Update urls.py with new app."""
    proj_dir = _find_project_dir(project_path)
    if not proj_dir:
        return

    urls_file = proj_dir / "urls.py"
    if not urls_file.exists():
        return

    content = urls_file.read_text()

    url_pattern = f'include("{app_name}.urls")'
    if url_pattern in content:
        return

    before_patterns = content.split("urlpatterns")[0] if "urlpatterns" in content else content
    has_include_import = "include" in before_patterns

    if "from django.urls import" in content:
        if has_include_import:
            pass
        elif "from django.urls import path" in content:
            content = content.replace(
                "from django.urls import path", "from django.urls import include, path"
            )
        elif "from django.urls import re_path" in content:
            content = content.replace(
                "from django.urls import re_path", "from django.urls import include, re_path"
            )
        else:
            content = content.replace("from django.urls import", "from django.urls import include,")
    else:
        content = "from django.urls import include, path\n" + content

    if (
        "urlpatterns = [" in content
        and f'path("{app_name}/"' not in content
        and f"path('{app_name}/'" not in content
    ):
        content = content.replace(
            "urlpatterns = [",
            f'urlpatterns = [\n    path("{app_name}/", include("{app_name}.urls")),',
        )

    urls_file.write_text(content)


def _create_app_urls(project_path: Path, app_name: str) -> None:
    """Create a basic urls.py for the app."""
    app_urls = project_path / app_name / "urls.py"
    if not app_urls.exists():
        url_content = """from django.urls import path
from . import views

urlpatterns = [
]
"""
        app_urls.write_text(url_content)


@app.get("/")
async def serve_index():
    """Serve the index page or API info."""
    ui_path = get_ui_path()
    if ui_path:
        index_path = ui_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path), media_type="text/html")

    return HTMLResponse("""
        <html>
        <head>
            <title>LazyDjango API</title>
            <style>
                body { font-family: monospace; background: #000; color: #fff; padding: 40px; }
                a { color: #fff; }
                pre { background: #111; padding: 20px; }
            </style>
        </head>
        <body>
            <h1>LazyDjango API</h1>
            <p>API is running. Build UI with: <code>cd ui && npm install && npm run build</code></p>
            <hr>
            <h2>Endpoints</h2>
            <pre>
GET  /api/health/
GET  /api/project/
GET  /api/project/apps/
POST /api/apps/create/
POST /api/models/create/
POST /api/views/create/
POST /api/admin/create/
POST /api/forms/create/
POST /api/auth/setup/
POST /api/static/setup/
POST /api/middleware/create/
POST /api/server/
            </pre>
        </body>
        </html>
    """)


@app.get("/api/")
async def api_info():
    """API information."""
    return {
        "name": "LazyDjango API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health/")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/api/health/")
async def api_health():
    """API health check."""
    return {"success": True, "message": "OK", "status": "healthy"}


@app.get("/api/project/")
async def project_info(project_path: str = "."):
    """Get project information with full details."""
    from lazydjango.utils.detector import DjangoProjectDetector

    try:
        safe_path = validate_project_path(project_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}") from e

    detector = DjangoProjectDetector(safe_path)
    detector.detect_full()

    if not detector.is_django_project:
        error_msg = (
            detector.last_error
            if detector.last_error
            else "Not a Django project. Ensure the path contains a Django project with settings.py and manage.py"
        )
        raise HTTPException(status_code=400, detail=error_msg)

    apps_data = []
    if detector.project:
        for app_name in detector.project.apps:
            app_info = detector.project.app_details.get(
                app_name, {"name": app_name, "models": [], "routes": []}
            )
            models = [
                (
                    {
                        "name": m.name,
                        "fields": [
                            {
                                "name": f.get("name", ""),
                                "type": f.get("type", ""),
                                "to": f.get("to", ""),
                            }
                            for f in (m.fields if hasattr(m, "fields") else [])
                        ],
                        "relationships": m.relationships if hasattr(m, "relationships") else [],
                    }
                    if hasattr(m, "name")
                    else {"name": str(m), "fields": [], "relationships": []}
                )
                for m in (app_info.models if hasattr(app_info, "models") else [])
            ]
            routes = [
                (
                    {"path": r.path, "view": r.view_name, "model": r.model_name}
                    if hasattr(r, "path")
                    else r
                )
                for r in (app_info.routes if hasattr(app_info, "routes") else [])
            ]
            apps_data.append(
                {
                    "name": app_name,
                    "models": models,
                    "routes": routes,
                }
            )

    return {
        "success": True,
        "message": "Project info",
        "data": {
            "path": str(detector.path),
            "name": str(detector.path).split("/")[-1],
            "apps": detector.project.apps if detector.project else [],
            "app_details": apps_data,
            "is_django": detector.is_django_project,
        },
    }


@app.get("/api/project/apps/")
async def list_apps(project_path: str = "."):
    """List all apps in project."""
    from lazydjango.utils.detector import DjangoProjectDetector

    try:
        safe_path = validate_project_path(project_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}") from e

    detector = DjangoProjectDetector(safe_path)
    detector.detect()

    if not detector.is_django_project:
        error_msg = detector.last_error if detector.last_error else "Not a Django project"
        raise HTTPException(status_code=400, detail=error_msg)

    return {
        "success": True,
        "message": "Apps list",
        "data": {
            "apps": detector.project.apps if detector.project else [],
        },
    }


@app.get("/api/bruno/")
async def get_bruno_docs(base_url: str = "http://localhost:8000"):
    """Get Bruno collection JSON for API documentation."""
    from lazydjango.generators.bruno_gen import generate_bruno_collection

    collection = generate_bruno_collection(base_url)
    return collection


@app.get("/api/bruno/download/")
async def download_bruno_docs(base_url: str = "http://localhost:8000"):
    """Download Bruno collection as JSON file."""
    from lazydjango.generators.bruno_gen import generate_bruno_collection

    collection = generate_bruno_collection(base_url)
    json_str = json.dumps(collection, indent=2)

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=lazydjango-bruno.json"},
    )


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    return Response(content=b"", media_type="image/x-icon")


@app.get("/_next/{path:path}")
async def serve_next_static(path: str):
    """Serve Next.js static files."""
    ui_path = get_ui_path()
    if not ui_path:
        raise HTTPException(status_code=404, detail="UI not found")

    file_path = ui_path / "_next" / path
    if file_path.exists() and file_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(str(file_path), media_type=mime_type or "application/octet-stream")
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve static files."""
    ui_path = get_ui_path()
    if not ui_path:
        raise HTTPException(status_code=404, detail="UI not found")

    file_path = ui_path / "static" / path
    if file_path.exists() and file_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(str(file_path), media_type=mime_type or "application/octet-stream")
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/{path:path}")
async def serve_ui_pages(path: str):
    """Serve UI pages."""
    ui_path = get_ui_path()
    if not ui_path:
        raise HTTPException(status_code=404, detail="UI not found")

    file_path = ui_path / path
    if file_path.exists() and file_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(str(file_path), media_type=mime_type or "text/html")

    index_path = ui_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")

    raise HTTPException(status_code=404, detail="Page not found")


def validate_identifier(value: str, field_name: str) -> str:
    """Validate that a value is a safe identifier."""
    if not value:
        return value
    if not SAFE_PATTERN.match(value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: '{value}'. Must be a valid Python identifier.",
        )
    return value


def validate_project_path(project_path: str) -> Path:
    """Validate and sanitize project path to prevent path traversal."""
    if project_path is None:
        return Path(".")

    if ".." in project_path:
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    return Path(project_path).resolve()


@app.post("/api/apps/create/")
async def create_app(request: AppCreateRequest):
    """Create a new Django app."""
    import subprocess
    import sys

    name = validate_identifier(request.name, "app name")

    try:
        project_path = validate_project_path(request.project_path or ".")
        result = subprocess.run(
            [sys.executable, "-m", "django", "startapp", name],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            _update_settings_with_app(project_path, name)
            _create_app_urls(project_path, name)
            _update_urls_with_app(project_path, name)
            return {
                "success": True,
                "message": f"App '{name}' created and registered",
                "data": {"app_name": name, "path": str(project_path / name)},
            }
        else:
            raise HTTPException(status_code=400, detail=f"Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/models/create/")
async def create_model(request: ModelCreateRequest):
    """Create a new Django model."""
    import subprocess
    import sys

    from lazydjango.generators.model_gen import ModelGenerator

    app_name = validate_identifier(request.app_name, "app name")
    model_name = validate_identifier(request.model_name, "model name")

    for field in request.fields:
        if field.name:
            validate_identifier(field.name, "field name")
        if field.related_model:
            parts = field.related_model.split(".")
            for p in parts:
                if p and p != "self":
                    validate_identifier(p, "related model")

    project_path = validate_project_path(request.project_path or ".")

    try:
        from lazydjango.api.models import FieldDefinition

        fields = [
            FieldDefinition(
                name=f.name,
                field_type=f.field_type,
                required=f.required,
                unique=f.unique,
                max_length=f.max_length,
                related_model=f.related_model,
                on_delete=f.on_delete,
            )
            for f in request.fields
            if f.name
        ]

        gen = ModelGenerator(
            app_name=app_name,
            model_name=model_name,
            fields=fields,
            project_path=project_path,
        )

        if not gen.generate():
            raise HTTPException(status_code=400, detail=f"Failed to create model '{model_name}'")

        result: dict[str, object] = {"model_name": model_name, "app_name": app_name}

        if request.migrate:
            makemigrations_result = subprocess.run(
                [sys.executable, "manage.py", "makemigrations", app_name],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if makemigrations_result.returncode != 0:
                raise HTTPException(
                    status_code=400, detail=f"Makemigrations failed: {makemigrations_result.stderr}"
                )

            migrate_result = subprocess.run(
                [sys.executable, "manage.py", "migrate"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if migrate_result.returncode != 0:
                raise HTTPException(
                    status_code=400, detail=f"Migrate failed: {migrate_result.stderr}"
                )
            result["migrated"] = True
            result["makemigrations_output"] = makemigrations_result.stdout
            result["migrate_output"] = migrate_result.stdout

        return {"success": True, "message": f"Model '{model_name}' created", "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/views/create/")
async def create_views(request: ViewCreateRequest):
    """Create views for a model."""
    from lazydjango.generators.view_gen import ViewGenerator

    app_name = validate_identifier(request.app_name, "app name")
    model_name = validate_identifier(request.model_name, "model name")
    project_path = validate_project_path(request.project_path or ".")

    gen = ViewGenerator(
        app_name=app_name,
        model_name=model_name,
        view_type=request.view_type,
        operations=request.operations,
        project_path=project_path,
    )

    if not gen.generate():
        raise HTTPException(status_code=400, detail=f"Failed to create views for '{model_name}'")

    return {
        "success": True,
        "message": f"Views for '{model_name}' created",
        "data": {"model_name": model_name, "app_name": app_name, "view_type": request.view_type},
    }


@app.post("/api/admin/create/")
async def create_admin(request: AdminCreateRequest):
    """Create admin configuration."""
    from lazydjango.generators.admin_gen import AdminGenerator

    app_name = validate_identifier(request.app_name, "app name")
    model_name = validate_identifier(request.model_name, "model name")
    project_path = validate_project_path(request.project_path or ".")

    gen = AdminGenerator(
        app_name=app_name,
        model_name=model_name,
        options={"list_display": True, "admin_theme": request.admin_theme},
        project_path=project_path,
    )

    if not gen.generate():
        raise HTTPException(status_code=400, detail=f"Failed to create admin for '{model_name}'")

    return {
        "success": True,
        "message": f"Admin for '{model_name}' created",
        "data": {"model_name": model_name, "app_name": app_name, "theme": request.admin_theme},
    }


@app.post("/api/forms/create/")
async def create_forms(request: FormCreateRequest):
    """Create forms and templates."""
    from lazydjango.generators.frontend_gen import FrontendGenerator

    app_name = validate_identifier(request.app_name, "app name")
    model_name = validate_identifier(request.model_name, "model name")
    project_path = validate_project_path(request.project_path or ".")

    gen = FrontendGenerator(
        app_name=app_name,
        model_name=model_name,
        gen_type=request.gen_type,
        style=request.style,
        project_path=project_path,
    )

    if not gen.generate():
        raise HTTPException(status_code=400, detail=f"Failed to create forms for '{model_name}'")

    return {
        "success": True,
        "message": f"Forms for '{model_name}' created",
        "data": {
            "model_name": model_name,
            "app_name": app_name,
            "gen_type": request.gen_type,
            "style": request.style,
        },
    }


@app.post("/api/auth/setup/")
async def setup_auth(request: AuthSetupRequest):
    """Setup JWT authentication."""
    from lazydjango.generators.auth_gen import AuthGenerator

    app_name = validate_identifier(request.app_name, "app name")
    project_path = validate_project_path(request.project_path or ".")

    gen = AuthGenerator(
        app_name=app_name,
        access_token_lifetime=request.access_token_lifetime,
        refresh_token_lifetime=request.refresh_token_lifetime,
        project_path=project_path,
    )

    if not gen.generate():
        raise HTTPException(status_code=400, detail="Failed to setup JWT Auth")

    return {
        "success": True,
        "message": "JWT Auth setup completed",
        "data": {
            "app_name": app_name,
            "access_lifetime": request.access_token_lifetime,
            "refresh_lifetime": request.refresh_token_lifetime,
        },
    }


@app.post("/api/static/setup/")
async def setup_static(request: StaticSetupRequest):
    """Setup static files/CSS framework."""
    from lazydjango.generators.static_gen import StaticGenerator

    project_path = validate_project_path(request.project_path or ".")

    gen = StaticGenerator(framework=request.framework, project_path=project_path)

    if not gen.generate():
        raise HTTPException(status_code=400, detail=f"Failed to setup {request.framework}")

    return {
        "success": True,
        "message": f"{request.framework} setup completed",
        "data": {"framework": request.framework},
    }


@app.post("/api/middleware/create/")
async def create_middleware(request: MiddlewareCreateRequest):
    """Create middleware."""
    from lazydjango.generators.middleware_gen import MiddlewareGenerator

    middleware_name = validate_identifier(request.middleware_name, "middleware name")
    project_path = validate_project_path(request.project_path or ".")

    gen = MiddlewareGenerator(
        middleware_name=middleware_name,
        middleware_type=request.middleware_type,
        custom_code=request.custom_code,
        project_path=project_path,
    )

    if not gen.generate():
        raise HTTPException(
            status_code=400, detail=f"Failed to create middleware '{middleware_name}'"
        )

    return {
        "success": True,
        "message": f"Middleware '{middleware_name}' created",
        "data": {"name": middleware_name, "type": request.middleware_type},
    }


@app.post("/api/server/")
async def server_command(request: ServerCommandRequest):
    """Execute server commands."""
    import subprocess
    import sys

    if request.command not in ALLOWED_COMMANDS:
        raise HTTPException(
            status_code=400, detail=f"Invalid command. Allowed: {', '.join(ALLOWED_COMMANDS)}"
        )

    project_path = validate_project_path(request.project_path or ".")
    result = {"command": request.command}

    try:
        if request.command == "start":
            port = max(1, min(65535, request.port))
            subprocess.Popen(
                [sys.executable, "manage.py", "runserver", f"0.0.0.0:{port}"],
                cwd=str(project_path),
            )
            return {"success": True, "message": f"Server started at 0.0.0.0:{port}", "data": result}

        elif request.command == "migrate":
            app_arg = []
            if request.app:
                app_name = validate_identifier(request.app, "app name")
                app_arg = [app_name]

            makemigrations_result = subprocess.run(
                [sys.executable, "manage.py", "makemigrations"] + app_arg,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=60,
            )

            migrate_result = subprocess.run(
                [sys.executable, "manage.py", "migrate"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": True,
                "message": "Migrations completed",
                "data": {
                    "command": request.command,
                    "makemigrations_output": makemigrations_result.stdout,
                    "migrate_output": migrate_result.stdout,
                    "makemigrations_returncode": makemigrations_result.returncode,
                    "migrate_returncode": migrate_result.returncode,
                },
            }

        elif request.command == "check":
            check_result = subprocess.run(
                [sys.executable, "manage.py", "check"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": True,
                "message": "Check completed",
                "data": {
                    "command": request.command,
                    "output": check_result.stdout,
                    "returncode": check_result.returncode,
                },
            }

        elif request.command == "shell":
            subprocess.Popen([sys.executable, "manage.py", "shell"], cwd=str(project_path))
            return {"success": True, "message": "Django shell opened", "data": result}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
