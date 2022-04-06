"""Bruno docs generator for LazyDjango API."""

import json
from pathlib import Path

API_ENDPOINTS = [
    {
        "folder": "01-Health",
        "requests": [
            {
                "name": "Health Check",
                "method": "GET",
                "url": "{{base_url}}/health/",
                "description": "Basic health check endpoint",
            },
            {
                "name": "API Health",
                "method": "GET",
                "url": "{{base_url}}/api/health/",
                "description": "API health check with status",
            },
        ],
    },
    {
        "folder": "02-Project",
        "requests": [
            {
                "name": "Get Project Info",
                "method": "GET",
                "url": "{{base_url}}/api/project/",
                "params": {"project_path": "."},
                "description": "Get project information with all apps, models, and routes",
            },
            {
                "name": "List Apps",
                "method": "GET",
                "url": "{{base_url}}/api/project/apps/",
                "params": {"project_path": "."},
                "description": "List all apps in the project",
            },
        ],
    },
    {
        "folder": "03-Apps",
        "requests": [
            {
                "name": "Create App",
                "method": "POST",
                "url": "{{base_url}}/api/apps/create/",
                "body": {"name": "myapp", "project_path": "."},
                "description": "Create a new Django app and register it",
            },
        ],
    },
    {
        "folder": "04-Models",
        "requests": [
            {
                "name": "Create Model",
                "method": "POST",
                "url": "{{base_url}}/api/models/create/",
                "body": {
                    "app_name": "myapp",
                    "model_name": "Product",
                    "fields": [
                        {"name": "name", "field_type": "CharField", "max_length": 255},
                        {"name": "price", "field_type": "DecimalField"},
                        {"name": "description", "field_type": "TextField", "required": False},
                    ],
                    "migrate": False,
                    "project_path": ".",
                },
                "description": "Create a Django model with fields",
            },
        ],
    },
    {
        "folder": "05-Views",
        "requests": [
            {
                "name": "Create Views",
                "method": "POST",
                "url": "{{base_url}}/api/views/create/",
                "body": {
                    "app_name": "myapp",
                    "model_name": "Product",
                    "view_type": "template",
                    "operations": {
                        "create": True,
                        "list": True,
                        "detail": True,
                        "update": True,
                        "delete": True,
                    },
                    "project_path": ".",
                },
                "description": "Create CRUD views for a model",
            },
        ],
    },
    {
        "folder": "06-Admin",
        "requests": [
            {
                "name": "Create Admin",
                "method": "POST",
                "url": "{{base_url}}/api/admin/create/",
                "body": {
                    "app_name": "myapp",
                    "model_name": "Product",
                    "admin_theme": "none",
                    "project_path": ".",
                },
                "description": "Create Django admin configuration",
            },
        ],
    },
    {
        "folder": "07-Forms",
        "requests": [
            {
                "name": "Create Forms",
                "method": "POST",
                "url": "{{base_url}}/api/forms/create/",
                "body": {
                    "app_name": "myapp",
                    "model_name": "Product",
                    "gen_type": "both",
                    "style": "bootstrap",
                    "project_path": ".",
                },
                "description": "Create Django forms and templates",
            },
        ],
    },
    {
        "folder": "08-Auth",
        "requests": [
            {
                "name": "Setup Auth",
                "method": "POST",
                "url": "{{base_url}}/api/auth/setup/",
                "body": {
                    "app_name": "users",
                    "access_token_lifetime": 60,
                    "refresh_token_lifetime": 7,
                    "project_path": ".",
                },
                "description": "Setup JWT authentication",
            },
        ],
    },
    {
        "folder": "09-Static",
        "requests": [
            {
                "name": "Setup Static",
                "method": "POST",
                "url": "{{base_url}}/api/static/setup/",
                "body": {"framework": "tailwind", "project_path": "."},
                "description": "Setup static files/CSS framework",
            },
        ],
    },
    {
        "folder": "10-Middleware",
        "requests": [
            {
                "name": "Create Middleware",
                "method": "POST",
                "url": "{{base_url}}/api/middleware/create/",
                "body": {
                    "middleware_name": "LoggingMiddleware",
                    "middleware_type": "logging",
                    "custom_code": "",
                    "project_path": ".",
                },
                "description": "Create custom middleware",
            },
        ],
    },
    {
        "folder": "11-Server",
        "requests": [
            {
                "name": "Start Server",
                "method": "POST",
                "url": "{{base_url}}/api/server/",
                "body": {"command": "start", "host": "0.0.0.0", "port": 8000, "project_path": "."},
                "description": "Start Django development server",
            },
            {
                "name": "Run Migrations",
                "method": "POST",
                "url": "{{base_url}}/api/server/",
                "body": {"command": "migrate", "app": "myapp", "project_path": "."},
                "description": "Run Django migrations",
            },
            {
                "name": "Check Project",
                "method": "POST",
                "url": "{{base_url}}/api/server/",
                "body": {"command": "check", "project_path": "."},
                "description": "Run Django system check",
            },
            {
                "name": "Open Shell",
                "method": "POST",
                "url": "{{base_url}}/api/server/",
                "body": {"command": "shell", "project_path": "."},
                "description": "Open Django shell",
            },
        ],
    },
]


def generate_bruno_collection(base_url: str = "http://localhost:8000") -> dict:
    """Generate Bruno collection JSON."""
    items = []

    for folder_data in API_ENDPOINTS:
        folder = {
            "name": folder_data["folder"],
            "type": "folder",
            "items": [],
        }

        for req in folder_data["requests"]:
            http_req = {
                "name": req["name"],
                "type": "http",
                "request": {
                    "method": req["method"],
                    "url": req["url"].replace("{{base_url}}", base_url),
                    "name": req["name"],
                },
            }

            if "params" in req:
                http_req["request"]["params"] = req["params"]

            if "body" in req:
                http_req["request"]["body"] = {
                    "type": "json",
                    "raw": json.dumps(req["body"], indent=2),
                }

            if "description" in req:
                http_req["request"]["description"] = req["description"]

            folder["items"].append(http_req)

        items.append(folder)

    return {
        "version": "1.0.0",
        "name": "LazyDjango API",
        "description": "Auto-generate Django code via REST API",
        "type": "collection",
        "items": items,
    }


def generate_bruno_folder(base_url: str = "http://localhost:8000") -> dict:
    """Generate individual .bru files for each request."""
    files = {}

    for folder_data in API_ENDPOINTS:
        folder_name = folder_data["folder"]
        files[folder_name] = []

        for req in folder_data["requests"]:
            filename = f"{req['name'].replace(' ', '-').lower()}.bru"
            content = []

            method = req["method"]
            url = req["url"].replace("{{base_url}}", base_url)
            content.append(f"meta {method} {url}")
            content.append("")

            if "params" in req:
                content.append("### params")
                for key, value in req["params"].items():
                    content.append(f"{key}: {value}")
                content.append("")

            if "body" in req:
                content.append("### body")
                content.append(req["body"])
                content.append("")

            if "description" in req:
                content.append("### description")
                content.append(req["description"])
                content.append("")

            files[folder_name].append({"filename": filename, "content": "\n".join(content)})

    return files


def save_bruno_docs(output_path: Path, base_url: str = "http://localhost:8000") -> bool:
    """Save Bruno docs to specified path."""
    try:
        output_path.mkdir(parents=True, exist_ok=True)

        collection = generate_bruno_collection(base_url)
        (output_path / "collection.json").write_text(json.dumps(collection, indent=2))

        files = generate_bruno_folder(base_url)
        for folder_name, requests in files.items():
            folder_path = output_path / folder_name
            folder_path.mkdir(exist_ok=True)
            for file_data in requests:
                (folder_path / file_data["filename"]).write_text(file_data["content"])

        return True
    except Exception as e:
        print(f"Error saving bruno docs: {e}")
        return False
