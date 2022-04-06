"""Auth generator - JWT setup."""

import contextlib
from pathlib import Path


class AuthGenerator:
    """Generates JWT authentication configuration."""

    def __init__(
        self,
        app_name: str = "users",
        access_token_lifetime: int = 60,
        refresh_token_lifetime: int = 7,
        project_path: Path | None = None,
        dry_run: bool = False,
    ):
        self.app_name = app_name
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime
        self.project_path = project_path or Path(".")
        self.dry_run = dry_run

    def generate(self) -> bool:
        """Setup JWT authentication."""
        try:
            if not self.dry_run:
                self._create_users_app()
                self._update_settings()
                self._update_urls()
                self._create_token_serializer()

            return True
        except Exception as e:
            print(f"Error setting up JWT auth: {e}")
            return False

    def _create_users_app(self) -> None:
        """Create users app if it doesn't exist."""
        import subprocess

        app_dir = self.project_path / self.app_name
        if not app_dir.exists():
            with contextlib.suppress(Exception):
                subprocess.run(
                    ["python", "manage.py", "startapp", self.app_name],
                    cwd=self.project_path,
                    capture_output=True,
                )

    def _update_settings(self) -> None:
        """Update Django settings."""
        settings_file = self.project_path / "settings.py"

        if not settings_file.exists():
            for item in self.project_path.iterdir():
                if item.is_dir():
                    settings_file = item / "settings.py"
                    if settings_file.exists():
                        break

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        if "'rest_framework'" not in content:
            content = content.replace(
                "INSTALLED_APPS = [",
                "INSTALLED_APPS = [\n    'rest_framework',\n    'rest_framework_simplejwt',",
            )
            settings_file.write_text(content)
            content = settings_file.read_text()

        if "REST_FRAMEWORK" not in content:
            rest_framework_config = f"""

from datetime import timedelta

REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}}

SIMPLE_JWT = {{
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes={self.access_token_lifetime}),
    'REFRESH_TOKEN_LIFETIME': timedelta(days={self.refresh_token_lifetime}),
    'AUTH_HEADER_TYPES': ('Bearer',),
}}
"""

            content += rest_framework_config

        settings_file.write_text(content)

    def _update_urls(self) -> None:
        """Update URL configuration."""
        try:
            urls_file = self.project_path / "urls.py"

            if not urls_file.exists():
                for item in self.project_path.iterdir():
                    if item.is_dir():
                        test_urls = item / "urls.py"
                        if test_urls.exists():
                            urls_file = test_urls
                            break

            if not urls_file.exists():
                return

            content = urls_file.read_text()

            if "rest_framework_simplejwt" not in content:
                from_text = "from django.urls import path"
                import_text = """from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView"""

                content = content.replace(from_text, import_text)

            if "token/" not in content:
                content = content.replace(
                    "urlpatterns = [",
                    "urlpatterns = [\n    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),\n    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),",
                )

            urls_file.write_text(content)

        except Exception as e:
            print(f"Error updating URLs: {e}")

    def _create_token_serializer(self) -> None:
        """Create custom token serializer."""
        serializers_file = self.project_path / self.app_name / "serializers.py"

        if serializers_file.exists():
            content = serializers_file.read_text()
            if "TokenSerializer" in content:
                return

        code = """
from rest_framework import serializers
from django.contrib.auth.models import User


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
"""

        if serializers_file.exists():
            with open(serializers_file, "a") as f:
                f.write(code)
        else:
            with open(serializers_file, "w") as f:
                f.write("from rest_framework import serializers\n\n")
                f.write(code)
