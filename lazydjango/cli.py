"""CLI entry point for lazydjango."""

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from lazydjango.api.models import FieldDefinition
from lazydjango.utils.detector import DjangoProjectDetector

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def get_detector(path: str) -> DjangoProjectDetector:
    """Get and validate detector for a Django project."""
    detector = DjangoProjectDetector(Path(path))
    detector.detect()

    if not detector.is_django_project:
        console.print(f"[red]Error:[/red] Not a Django project at [cyan]{path}[/cyan]")
        console.print(
            "[yellow]Make sure you're in a directory with manage.py and settings.py[/yellow]"
        )
        sys.exit(1)

    return detector


def run_command(
    cmd: list[str], cwd: str, capture: bool = True, verbose: bool = False
) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except Exception as e:
        return 1, "", str(e)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0", prog_name="lazydjango")
def main() -> None:
    """lazydjango - Auto-generate Django code via CLI."""
    pass


@main.command("init")
@click.option("--name", "-n", required=True, help="Project name")
@click.option("--template", "-t", default="default", help="Project template")
@click.argument("path", default=".")
def init(name: str, template: str, path: str) -> None:
    """Initialize a new Django project."""
    console.print(f"\n[bold cyan]Creating Django project:[/bold cyan] {name}")

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Running django-admin startproject...", total=None)
        code, stdout, stderr = run_command(
            [sys.executable, "-m", "django", "startproject", name, path], cwd=path, verbose=True
        )
        progress.update(task, completed=True)

    if code == 0:
        console.print(f"[green]✓[/green] Project '{name}' created successfully!")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  cd {name}")
        console.print("  python manage.py migrate")
        console.print("  python manage.py runserver")
    else:
        console.print("[red]✗[/red] Failed to create project")
        console.print(f"[red]{stderr}[/red]")
        sys.exit(1)


@main.group("model")
def model() -> None:
    """Model-related commands."""
    pass


@model.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--app", "-a", required=True, help="App name")
@click.option("--name", "-n", required=True, help="Model name")
@click.option("--migrate/--no-migrate", default=False, help="Run migrations after creating model")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def model_create(
    path: str, app: str, name: str, migrate: bool, verbose: bool, dry_run: bool
) -> None:
    """Create a new Django model."""
    get_detector(path)
    from lazydjango.generators.model_gen import ModelGenerator

    if not name[0].isupper():
        console.print(
            "[yellow]Warning:[/yellow] Model name should be PascalCase (e.g., 'Product', not 'product')"
        )
        name = name.title()

    fields = _prompt_fields(path)

    if not fields:
        console.print("[red]No fields added. Aborting.[/red]")
        sys.exit(1)

    _print_model_summary(app, name, fields)

    if not click.confirm("\nCreate this model?"):
        console.print("Cancelled.")
        return

    if verbose:
        console.print(f"\n[cyan]Creating model '{name}' in app '{app}'...[/cyan]")

    gen = ModelGenerator(
        app_name=app,
        model_name=name,
        fields=fields,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] Model '{name}' created successfully!")

        if migrate:
            console.print("\n[cyan]Running migrations...[/cyan]")
            run_command(
                [sys.executable, "manage.py", "makemigrations", app], cwd=path, verbose=verbose
            )
            code, stdout, stderr = run_command(
                [sys.executable, "manage.py", "migrate"], cwd=path, verbose=verbose
            )

            if code == 0:
                console.print("[green]✓[/green] Migrations completed!")
            else:
                console.print(f"[red]Migration error:[/red] {stderr}")
    else:
        console.print(f"[red]✗[/red] Failed to create model '{name}'")
        sys.exit(1)


@model.command("list")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def model_list(path: str, verbose: bool) -> None:
    """List all models in the project."""
    detector = get_detector(path)

    table = Table(title="Django Models")
    table.add_column("App", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Fields", style="yellow")

    for app_name in detector.project.apps:
        models = detector.get_existing_models(app_name)
        for model_name in models:
            table.add_row(app_name, model_name, "-")

    console.print(table)


def _prompt_fields(project_path: str) -> list[FieldDefinition]:
    """Interactively prompt for model fields."""
    fields = []

    field_types = [
        ("1", "CharField", "Short text (max 255 chars)"),
        ("2", "TextField", "Long text"),
        ("3", "IntegerField", "Integer number"),
        ("4", "PositiveIntegerField", "Positive integer"),
        ("5", "BigIntegerField", "Large integer"),
        ("6", "FloatField", "Decimal number"),
        ("7", "DecimalField", "Precise decimal (for money)"),
        ("8", "BooleanField", "True/False"),
        ("9", "DateField", "Date only"),
        ("10", "DateTimeField", "Date and time"),
        ("11", "TimeField", "Time only"),
        ("12", "EmailField", "Email address"),
        ("13", "URLField", "Website URL"),
        ("14", "FileField", "File upload"),
        ("15", "ImageField", "Image upload"),
        ("16", "ForeignKey", "Relation to another model"),
        ("17", "OneToOneField", "One-to-one relation"),
        ("18", "ManyToManyField", "Many-to-many relation"),
        ("19", "UUIDField", "Unique identifier"),
        ("20", "JSONField", "JSON data"),
    ]

    on_delete_options = [
        ("1", "CASCADE", "Delete related objects"),
        ("2", "PROTECT", "Prevent deletion"),
        ("3", "SET_NULL", "Set to NULL"),
        ("4", "SET_DEFAULT", "Set to default"),
        ("5", "DO_NOTHING", "No action"),
    ]

    console.print("\n[bold]Add Model Fields[/bold]")
    console.print("Press Enter on empty name to finish\n")

    while True:
        console.print("[bold]--- New Field ---[/bold]")
        field_name = click.prompt("Field name (snake_case)", default="", show_default=False)

        if not field_name:
            if fields:
                break
            console.print("[yellow]Add at least one field![/yellow]")
            continue

        console.print("\n[bold]Select Field Type:[/bold]")
        for num, name, desc in field_types:
            console.print(f"  [{num}] {name}: {desc}")

        while True:
            choice = click.prompt("Enter number", default="1", show_default=False)
            if choice.isdigit() and 1 <= int(choice) <= len(field_types):
                field_type = field_types[int(choice) - 1][1]
                break
            console.print("[red]Invalid choice. Try again.[/red]")

        opts = {"required": True, "unique": False}

        if field_type == "CharField":
            opts["max_length"] = click.prompt("  Max length", default=255, type=int)

        if field_type == "DecimalField":
            opts["max_digits"] = click.prompt("  Max digits", default=10, type=int)
            opts["decimal_places"] = click.prompt("  Decimal places", default=2, type=int)

        opts["required"] = click.confirm("  Required field?", default=True)
        opts["unique"] = click.confirm("  Unique field?", default=False)

        if field_type in ("ForeignKey", "OneToOneField", "ManyToManyField"):
            detector = get_detector(project_path)
            related_models = []

            for app in detector.project.apps if detector.project else []:
                for m in detector.get_existing_models(app):
                    related_models.append(f"{app}.{m}")

            if related_models:
                console.print("\n[bold]Select Related Model:[/bold]")
                for i, rm in enumerate(related_models, 1):
                    console.print(f"  [{i}] {rm}")

                while True:
                    choice = click.prompt("Enter number", default="1", show_default=False)
                    if choice.isdigit() and 1 <= int(choice) <= len(related_models):
                        opts["related_model"] = related_models[int(choice) - 1]
                        break
                    console.print("[red]Invalid choice. Try again.[/red]")
            else:
                opts["related_model"] = click.prompt(
                    "  Related model (e.g., 'app.Model')", default=""
                )

            if field_type == "ForeignKey":
                console.print("\n[bold]On Delete Action:[/bold]")
                for num, name, desc in on_delete_options:
                    console.print(f"  [{num}] {name}: {desc}")

                while True:
                    choice = click.prompt("Enter number", default="1", show_default=False)
                    if choice.isdigit() and 1 <= int(choice) <= len(on_delete_options):
                        opts["on_delete"] = on_delete_options[int(choice) - 1][1]
                        break
                    console.print("[red]Invalid choice. Try again.[/red]")

        fd = FieldDefinition(
            name=field_name,
            field_type=field_type,
            required=opts.get("required", True),
            unique=opts.get("unique", False),
            max_length=opts.get("max_length"),
            related_model=opts.get("related_model"),
            on_delete=opts.get("on_delete", "CASCADE"),
        )
        fields.append(fd)

        console.print(f"[green]✓[/green] Field '{field_name}' added!\n")

        if not click.confirm("Add another field?", default=True):
            break

    return fields


def _print_model_summary(app: str, name: str, fields: list[FieldDefinition]) -> None:
    """Print a summary of the model to be created."""
    console.print("\n[bold]Model Summary:[/bold]")
    console.print(f"  App: [cyan]{app}[/cyan]")
    console.print(f"  Model: [green]{name}[/green]")
    console.print(f"  Fields: [yellow]{len(fields)}[/yellow]")

    for f in fields:
        extras = []
        if f.max_length:
            extras.append(f"max_length={f.max_length}")
        if f.related_model:
            extras.append(f"-> {f.related_model}")
        extra_str = f" ({', '.join(extras)})" if extras else ""
        req = " (required)" if f.required else " (optional)"
        console.print(f"    - [blue]{f.name}[/blue]: {f.field_type}{extra_str}{req}")


@main.group("app")
def app_cmd() -> None:
    """App-related commands."""
    pass


@app_cmd.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.argument("name")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def app_create(path: str, name: str, verbose: bool) -> None:
    """Create a new Django app."""
    get_detector(path)

    if not name.isidentifier():
        console.print(f"[red]Error:[/red] '{name}' is not a valid app name")
        sys.exit(1)

    console.print(f"[cyan]Creating app '{name}'...[/cyan]")

    code, stdout, stderr = run_command(
        [sys.executable, "manage.py", "startapp", name], cwd=path, verbose=verbose
    )

    if code == 0:
        console.print(f"[green]✓[/green] App '{name}' created successfully!")
    else:
        console.print(f"[red]✗[/red] Error: {stderr}")
        sys.exit(1)


@app_cmd.command("list")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def app_list(path: str, verbose: bool) -> None:
    """List all apps in the project."""
    detector = get_detector(path)

    table = Table(title="Django Apps")
    table.add_column("App Name", style="cyan")
    table.add_column("Status", style="green")

    for app_name in detector.project.apps:
        table.add_row(app_name, "✓ Installed")

    console.print(table)


@main.group("view")
def view() -> None:
    """View-related commands."""
    pass


@view.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--app", "-a", required=True, help="App name")
@click.option("--model", "-m", required=True, help="Model name")
@click.option(
    "--type",
    "-t",
    "view_type",
    type=click.Choice(["template", "api", "viewset"]),
    default="template",
    help="View type",
)
@click.option(
    "--operations",
    "-o",
    multiple=True,
    type=click.Choice(["create", "list", "detail", "update", "delete"]),
    default=["create", "list", "detail", "update", "delete"],
    help="Operations to generate",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def view_create(
    path: str, app: str, model: str, view_type: str, operations: tuple, verbose: bool, dry_run: bool
) -> None:
    """Create views for a model."""
    get_detector(path)
    from lazydjango.generators.view_gen import ViewGenerator

    ops = dict.fromkeys(["create", "list", "detail", "update", "delete"], True)
    for op in operations:
        ops[op] = True

    console.print(f"[cyan]Creating views for '{model}' in app '{app}'...[/cyan]")

    gen = ViewGenerator(
        app_name=app,
        model_name=model,
        view_type=view_type,
        operations=ops,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] Views for '{model}' created successfully!")
    else:
        console.print(f"[red]✗[/red] Failed to create views for '{model}'")
        sys.exit(1)


@main.group("admin")
def admin() -> None:
    """Admin-related commands."""
    pass


@admin.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--app", "-a", required=True, help="App name")
@click.option("--model", "-m", required=True, help="Model name")
@click.option(
    "--theme",
    "-t",
    type=click.Choice(["none", "unfold", "jet", "adminlte", "tabler"]),
    default="none",
    help="Admin theme",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def admin_create(path: str, app: str, model: str, theme: str, verbose: bool, dry_run: bool) -> None:
    """Create admin configuration for a model."""
    get_detector(path)
    from lazydjango.generators.admin_gen import AdminGenerator

    console.print(f"[cyan]Creating admin for '{model}' in app '{app}'...[/cyan]")

    gen = AdminGenerator(
        app_name=app,
        model_name=model,
        options={"list_display": True, "admin_theme": theme},
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] Admin for '{model}' created successfully!")
    else:
        console.print(f"[red]✗[/red] Failed to create admin for '{model}'")
        sys.exit(1)


@main.group("form")
def form() -> None:
    """Form-related commands."""
    pass


@form.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--app", "-a", required=True, help="App name")
@click.option("--model", "-m", required=True, help="Model name")
@click.option(
    "--type",
    "-t",
    "form_type",
    type=click.Choice(["both", "form", "template"]),
    default="both",
    help="What to generate",
)
@click.option(
    "--style",
    "-s",
    type=click.Choice(["bootstrap", "tailwind", "plain"]),
    default="bootstrap",
    help="Template style",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def form_create(
    path: str, app: str, model: str, form_type: str, style: str, verbose: bool, dry_run: bool
) -> None:
    """Create forms and templates for a model."""
    get_detector(path)
    from lazydjango.generators.frontend_gen import FrontendGenerator

    console.print(f"[cyan]Creating forms/templates for '{model}' in app '{app}'...[/cyan]")

    gen = FrontendGenerator(
        app_name=app,
        model_name=model,
        gen_type=form_type,
        style=style,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] Forms/templates for '{model}' created successfully!")
    else:
        console.print(f"[red]✗[/red] Failed to create forms for '{model}'")
        sys.exit(1)


@main.group("auth")
def auth() -> None:
    """Authentication-related commands."""
    pass


@auth.command("setup")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option(
    "--access-lifetime", "-a", default=60, type=int, help="Access token lifetime in minutes"
)
@click.option(
    "--refresh-lifetime", "-r", default=7, type=int, help="Refresh token lifetime in days"
)
@click.option("--app-name", default="users", help="App name for users")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def auth_setup(
    path: str,
    access_lifetime: int,
    refresh_lifetime: int,
    app_name: str,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Setup JWT authentication."""
    get_detector(path)
    from lazydjango.generators.auth_gen import AuthGenerator

    console.print("[cyan]Setting up JWT authentication...[/cyan]")

    gen = AuthGenerator(
        app_name=app_name,
        access_token_lifetime=access_lifetime,
        refresh_token_lifetime=refresh_lifetime,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print("[green]✓[/green] JWT authentication setup completed!")
        console.print("\n[bold]Note:[/bold] You may need to install dependencies:")
        console.print("  pip install djangorestframework djangorestframework-simplejwt")
    else:
        console.print("[red]✗[/red] Failed to setup JWT authentication")
        sys.exit(1)


@main.group("static")
def static() -> None:
    """Static files commands."""
    pass


@static.command("setup")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["tailwind", "bootstrap"]),
    required=True,
    help="CSS framework",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def static_setup(path: str, framework: str, verbose: bool, dry_run: bool) -> None:
    """Setup static files/CSS framework."""
    get_detector(path)
    from lazydjango.generators.static_gen import StaticGenerator

    console.print(f"[cyan]Setting up {framework}...[/cyan]")

    gen = StaticGenerator(
        framework=framework,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] {framework} setup completed!")
    else:
        console.print(f"[red]✗[/red] Failed to setup {framework}")
        sys.exit(1)


@main.group("middleware")
def middleware() -> None:
    """Middleware-related commands."""
    pass


@middleware.command("create")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--name", "-n", required=True, help="Middleware name")
@click.option(
    "--type",
    "-t",
    "middleware_type",
    type=click.Choice(["logging", "auth", "rate_limit", "cors", "custom"]),
    default="custom",
    help="Middleware type",
)
@click.option("--code", "-c", default="", help="Custom code for custom middleware")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def middleware_create(
    path: str, name: str, middleware_type: str, code: str, verbose: bool, dry_run: bool
) -> None:
    """Create a middleware."""
    get_detector(path)
    from lazydjango.generators.middleware_gen import MiddlewareGenerator

    console.print(f"[cyan]Creating middleware '{name}'...[/cyan]")

    gen = MiddlewareGenerator(
        middleware_name=name,
        middleware_type=middleware_type,
        custom_code=code,
        project_path=Path(path),
        dry_run=dry_run,
    )

    if gen.generate():
        console.print(f"[green]✓[/green] Middleware '{name}' created successfully!")
    else:
        console.print(f"[red]✗[/red] Failed to create middleware '{name}'")
        sys.exit(1)


@main.group("server")
def server() -> None:
    """Server-related commands."""
    pass


@server.command("start")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def server_start(path: str, host: str, port: int, verbose: bool) -> None:
    """Start the Django development server."""
    get_detector(path)
    console.print(f"[green]Starting Django server at http://{host}:{port}[/green]")
    run_command(
        [sys.executable, "manage.py", "runserver", f"{host}:{port}"], cwd=path, capture=False
    )


@server.command("migrate")
@click.option("--path", "-p", default=".", help="Django project path")
@click.argument("app", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def server_migrate(path: str, app: str | None, verbose: bool) -> None:
    """Run Django migrations."""
    get_detector(path)

    if app:
        console.print(f"[cyan]Creating migrations for '{app}'...[/cyan]")
        code1, _, stderr1 = run_command(
            [sys.executable, "manage.py", "makemigrations", app], cwd=path, verbose=verbose
        )
        if code1 != 0:
            console.print(f"[red]Error creating migrations:[/red] {stderr1}")
            sys.exit(1)
    else:
        console.print("[cyan]Creating migrations...[/cyan]")
        code1, _, stderr1 = run_command(
            [sys.executable, "manage.py", "makemigrations"], cwd=path, verbose=verbose
        )
        if code1 != 0:
            console.print(f"[red]Error creating migrations:[/red] {stderr1}")
            sys.exit(1)

    console.print("[cyan]Applying migrations...[/cyan]")
    code2, stdout, stderr2 = run_command(
        [sys.executable, "manage.py", "migrate"], cwd=path, verbose=verbose
    )

    if code2 == 0:
        console.print("[green]✓[/green] Migrations completed!")
    else:
        console.print(f"[red]Error applying migrations:[/red] {stderr2}")
        sys.exit(1)


@server.command("check")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def server_check(path: str, verbose: bool) -> None:
    """Run Django system checks."""
    get_detector(path)
    console.print("[cyan]Running Django system checks...[/cyan]")

    code, stdout, stderr = run_command(
        [sys.executable, "manage.py", "check"], cwd=path, verbose=True
    )

    if stdout:
        console.print(stdout)
    if stderr:
        console.print(f"[yellow]{stderr}[/yellow]")

    if code == 0:
        console.print("[green]✓[/green] All checks passed!")
    else:
        console.print("[red]✗[/red] Checks failed")
        sys.exit(code)


@server.command("shell")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def server_shell(path: str, verbose: bool) -> None:
    """Open Django shell."""
    get_detector(path)
    console.print("[cyan]Opening Django shell...[/cyan]")
    run_command([sys.executable, "manage.py", "shell"], cwd=path, capture=False)


@main.command("info")
@click.option("--path", "-p", default=".", help="Django project path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def info(path: str, verbose: bool) -> None:
    """Show Django project information."""
    detector = get_detector(path)
    project = detector.project

    table = Table(title="Django Project Info", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Path", str(project.root))
    table.add_row("Project Name", project.project_name)
    table.add_row("Settings", str(project.settings_path))
    table.add_row("Apps", ", ".join(project.apps) if project.apps else "None")

    console.print(table)


@main.command("web")
@click.option("--port", "-p", default=6767, type=int, help="Port to run the web server")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--api-only", is_flag=True, help="Run only the API server (no UI)")
def web(port: int, host: str, api_only: bool) -> None:
    """Start the web server with UI and API."""
    import uvicorn

    ui_path = Path(__file__).parent / "ui" / "out"
    has_ui = ui_path.exists()

    console.print(Panel.fit("[bold]LazyDjango Web Server[/bold]", border_style="cyan"))

    if api_only:
        console.print(f"API:     [cyan]http://{host}:{port}[/cyan]")
        console.print(f"API Docs: [cyan]http://{host}:{port}/docs[/cyan]")
    elif has_ui:
        console.print(f"UI:      [cyan]http://{host}:{port}[/cyan]")
        console.print(f"API:     [cyan]http://{host}:{port}/api/health[/cyan]")
        console.print(f"API Docs: [cyan]http://{host}:{port}/docs[/cyan]")
    else:
        console.print(f"API:     [cyan]http://{host}:{port}[/cyan]")
        console.print(f"API Docs: [cyan]http://{host}:{port}/docs[/cyan]")
        console.print("\n[yellow]Note:[/yellow] UI not built. API only mode.")

    console.print("\n[dim]Press Ctrl+C to stop[/dim]")

    from lazydjango.api.views import app as api_app

    uvicorn.run(api_app, host=host, port=port, reload=False)


@main.command("api-docs")
def api_docs() -> None:
    """Show information about the API documentation."""
    console.print(Panel.fit("[bold]LazyDjango API Documentation[/bold]", border_style="cyan"))

    console.print("\n[bold]Available Resources:[/bold]")
    console.print("  [cyan]Bruno Collection:[/cyan] bruno/collection.json")
    console.print("  [cyan]OpenAPI Docs:[/cyan]    http://localhost:6767/docs")
    console.print("  [cyan]ReDoc:[/cyan]           http://localhost:6767/redoc")

    console.print("\n[bold]To start the API server, run:[/bold]")
    console.print("  [green]lazydjango web[/green]")


if __name__ == "__main__":
    main()
