"""API Pydantic models for lazydjango."""

from pydantic import BaseModel, Field


class FieldDefinition(BaseModel):
    """Model for field definition."""

    name: str
    field_type: str = "CharField"
    required: bool = True
    unique: bool = False
    blank: bool = False
    max_length: int | None = None
    default: str | None = None
    related_model: str | None = None
    related_name: str | None = None
    on_delete: str = "CASCADE"


class ModelCreateRequest(BaseModel):
    """Request model for creating a model."""

    app_name: str
    model_name: str
    fields: list[FieldDefinition] = Field(default_factory=list)
    migrate: bool = False
    project_path: str | None = "."


class ViewCreateRequest(BaseModel):
    """Request model for creating views."""

    app_name: str
    model_name: str
    view_type: str = "template"
    operations: dict = Field(
        default_factory=lambda: {
            "create": True,
            "list": True,
            "detail": True,
            "update": True,
            "delete": True,
        }
    )
    project_path: str | None = "."


class AdminCreateRequest(BaseModel):
    """Request model for creating admin."""

    app_name: str
    model_name: str
    admin_theme: str = "none"
    project_path: str | None = "."


class FormCreateRequest(BaseModel):
    """Request model for creating forms."""

    app_name: str
    model_name: str
    gen_type: str = "both"
    style: str = "bootstrap"
    project_path: str | None = "."


class AuthSetupRequest(BaseModel):
    """Request model for auth setup."""

    app_name: str = "users"
    access_token_lifetime: int = 60
    refresh_token_lifetime: int = 7
    project_path: str | None = "."


class StaticSetupRequest(BaseModel):
    """Request model for static setup."""

    framework: str
    project_path: str | None = "."


class MiddlewareCreateRequest(BaseModel):
    """Request model for middleware creation."""

    middleware_name: str
    middleware_type: str = "custom"
    custom_code: str = ""
    project_path: str | None = "."


class ServerCommandRequest(BaseModel):
    """Request model for server commands."""

    command: str
    app: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    project_path: str | None = "."


class AppCreateRequest(BaseModel):
    """Request model for app creation."""

    name: str
    project_path: str | None = "."
