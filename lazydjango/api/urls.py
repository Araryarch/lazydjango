"""API URL Configuration."""

from django.urls import path

from .views import (
    create_admin,
    create_app,
    create_forms,
    create_middleware,
    create_model,
    create_views,
    health_check,
    list_apps,
    project_info,
    server_command,
    setup_auth,
    setup_static,
)

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("project/", project_info, name="project_info"),
    path("project/apps/", list_apps, name="list_apps"),
    path("apps/create/", create_app, name="create_app"),
    path("models/create/", create_model, name="create_model"),
    path("views/create/", create_views, name="create_views"),
    path("admin/create/", create_admin, name="create_admin"),
    path("forms/create/", create_forms, name="create_forms"),
    path("auth/setup/", setup_auth, name="setup_auth"),
    path("static/setup/", setup_static, name="setup_static"),
    path("middleware/create/", create_middleware, name="create_middleware"),
    path("server/", server_command, name="server_command"),
]
