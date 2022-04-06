# lazydjango

[![Cross-Platform Tests](https://github.com/Araryarch/lazydjango/workflows/Cross-Platform%20Tests/badge.svg)](https://github.com/Araryarch/lazydjango/actions)
[![PyPI Version](https://img.shields.io/pypi/v/lazydjango.svg)](https://pypi.org/project/lazydjango/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Auto-generate Django code via CLI or Web API - Models, Views, Admin, Forms, Auth, Middleware

## Features

### Code Generation
- **Model Generator** - Create Django models with fields (CharField, TextField, ForeignKey, ManyToManyField, etc.)
- **View Generator** - Auto-generate CRUD API views (list, create, detail, update, delete)
- **Admin Generator** - Generate Django admin configuration with list_display
- **Form Generator** - Create Django ModelForms and HTML templates
- **JWT Auth Setup** - Auto configure SimpleJWT authentication
- **Static Setup** - Auto configure TailwindCSS or Bootstrap 5
- **Middleware Generator** - Generate custom middleware (logging, auth, rate limit, CORS)
- **App Generator** - Create new Django apps with automatic registration

### API Server
- **FastAPI-powered REST API** - All features accessible via HTTP endpoints
- **Built-in Web UI** - Modern dark-themed Next.js interface (included in wheel)
- **Project Detection** - Auto-detect existing Django projects with models and relationships
- **Database/ERD Tab** - Visualize models and relationships in your project

### Developer Experience
- **Bruno Docs** - Auto-generate Bruno collection for API testing
- **CLI Mode** - Command-line interface for scripting and automation

## Installation

```bash
pip install lazydjango
```

With development tools:
```bash
pip install lazydjango[dev]
```

## Usage

### Web UI (Recommended)
```bash
lazydjango web
# Then open http://localhost:8000
```

### API Only
```bash
lazydjango web --api-only
# API available at http://localhost:8000/api/
```

### CLI
```bash
lazydjango create-app blog
lazydjango create-model blog.Post title content
lazydjango create-views blog.Post --operations list,create,detail,update,delete
lazydjango create-admin blog.Post
lazydjango server start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check |
| GET | `/api/project/` | Get project info with models |
| GET | `/api/project/apps/` | List all apps |
| POST | `/api/apps/create/` | Create new app |
| POST | `/api/models/create/` | Create model with fields |
| POST | `/api/views/create/` | Create CRUD views |
| POST | `/api/admin/create/` | Create admin config |
| POST | `/api/forms/create/` | Create forms & templates |
| POST | `/api/auth/setup/` | Setup JWT auth |
| POST | `/api/static/setup/` | Setup static files |
| POST | `/api/middleware/create/` | Create middleware |
| POST | `/api/server/` | Run Django commands |
| GET | `/api/bruno/` | Get Bruno collection |
| GET | `/api/bruno/download/` | Download Bruno JSON |

## API Request Examples

### Create App
```bash
curl -X POST http://localhost:8000/api/apps/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "blog", "project_path": "."}'
```

### Create Model
```bash
curl -X POST http://localhost:8000/api/models/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "blog",
    "model_name": "Post",
    "fields": [
      {"name": "title", "field_type": "CharField", "max_length": 255},
      {"name": "content", "field_type": "TextField"}
    ],
    "migrate": true,
    "project_path": "."
  }'
```

### Create Model with ForeignKey
```bash
curl -X POST http://localhost:8000/api/models/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "blog",
    "model_name": "Comment",
    "fields": [
      {"name": "text", "field_type": "TextField"},
      {"name": "post", "field_type": "ForeignKey", "related_model": "blog.Post", "on_delete": "CASCADE"}
    ],
    "migrate": true,
    "project_path": "."
  }'
```

### Create Views
```bash
curl -X POST http://localhost:8000/api/views/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "blog",
    "model_name": "Post",
    "view_type": "template",
    "operations": {
      "create": true,
      "list": true,
      "detail": true,
      "update": true,
      "delete": true
    },
    "project_path": "."
  }'
```

### Run Django Commands
```bash
# Check project
curl -X POST http://localhost:8000/api/server/ \
  -H "Content-Type: application/json" \
  -d '{"command": "check", "project_path": "."}'

# Run migrations
curl -X POST http://localhost:8000/api/server/ \
  -H "Content-Type: application/json" \
  -d '{"command": "migrate", "project_path": "."}'
```

## Testing with Bruno

Download Bruno collection:
```bash
curl -o lazydjango-bruno.json http://localhost:8000/api/bruno/download/
```

Or import from the `bruno/` folder included in the package.

## Requirements

- Python 3.10+
- Django 4.2+
- FastAPI
- Uvicorn

## License

MIT License
