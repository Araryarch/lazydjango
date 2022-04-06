"""API Serializers for lazydjango."""

from rest_framework import serializers


class FieldDefinitionSerializer(serializers.Serializer):
    """Serializer for field definition."""

    name = serializers.CharField()
    field_type = serializers.CharField()
    required = serializers.BooleanField(default=True)
    unique = serializers.BooleanField(default=False)
    max_length = serializers.IntegerField(required=False, allow_null=True)
    related_model = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    on_delete = serializers.CharField(default="CASCADE")


class ModelCreateSerializer(serializers.Serializer):
    """Serializer for model creation."""

    app_name = serializers.CharField(required=True)
    model_name = serializers.CharField(required=True)
    fields = FieldDefinitionSerializer(many=True, required=False, default=list)
    migrate = serializers.BooleanField(default=False)


class ViewCreateSerializer(serializers.Serializer):
    """Serializer for view creation."""

    app_name = serializers.CharField(required=True)
    model_name = serializers.CharField(required=True)
    view_type = serializers.ChoiceField(choices=["template", "api", "viewset"], default="template")
    operations = serializers.DictField(required=False, default=dict)


class AdminCreateSerializer(serializers.Serializer):
    """Serializer for admin creation."""

    app_name = serializers.CharField(required=True)
    model_name = serializers.CharField(required=True)
    admin_theme = serializers.ChoiceField(
        choices=["none", "unfold", "jet", "adminlte", "tabler"], default="none"
    )


class FormCreateSerializer(serializers.Serializer):
    """Serializer for form/template creation."""

    app_name = serializers.CharField(required=True)
    model_name = serializers.CharField(required=True)
    gen_type = serializers.ChoiceField(choices=["both", "form", "template"], default="both")
    style = serializers.ChoiceField(choices=["bootstrap", "tailwind", "plain"], default="bootstrap")


class AuthSetupSerializer(serializers.Serializer):
    """Serializer for JWT auth setup."""

    app_name = serializers.CharField(default="users")
    access_token_lifetime = serializers.IntegerField(default=60)
    refresh_token_lifetime = serializers.IntegerField(default=7)


class StaticSetupSerializer(serializers.Serializer):
    """Serializer for static files setup."""

    framework = serializers.ChoiceField(choices=["tailwind", "bootstrap"], required=True)


class MiddlewareCreateSerializer(serializers.Serializer):
    """Serializer for middleware creation."""

    middleware_name = serializers.CharField(required=True)
    middleware_type = serializers.ChoiceField(
        choices=["logging", "auth", "rate_limit", "cors", "custom"], default="custom"
    )
    custom_code = serializers.CharField(required=False, allow_blank=True, default="")


class ServerCommandSerializer(serializers.Serializer):
    """Serializer for server commands."""

    command = serializers.ChoiceField(
        choices=["start", "stop", "migrate", "check", "shell"], required=True
    )
    app = serializers.CharField(required=False, allow_blank=True)
    host = serializers.CharField(default="0.0.0.0")
    port = serializers.IntegerField(default=8000)


class AppCreateSerializer(serializers.Serializer):
    """Serializer for app creation."""

    name = serializers.CharField(required=True)
