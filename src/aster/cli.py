import asyncio
from typing import Annotated, Callable

import typer

import aster

app = typer.Typer(help="Providing configuration, server, database commands for aster.")
database_app = typer.Typer()
server_app = typer.Typer()

app.add_typer(
    database_app,
    name="database",
    help="Contains all aster database-related commands (init, heads, history, upgrade, drop).",
)
app.add_typer(
    server_app,
    name="server",
    help="Contains all aster server-related commands (start, config)",
)


def version_callback(show_version: bool) -> None:
    if show_version:
        typer.echo(f"aster {aster.ASTER_VERSION}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Print aster version",
            callback=version_callback,
        ),
    ] = False
) -> None:
    ...


@database_app.command("init", help="Initializes a new database.")
def database_init() -> None:
    from .database import engine, init_database

    typer.echo("Initializing new database...")
    asyncio.run(init_database(engine))
    typer.secho("Success.", fg="green")


@database_app.command("drop", help="Drops all data in database.")
def database_drop(
    yes: Annotated[
        bool, typer.Option(help="Silences all confirmation prompts.")
    ] = False
) -> None:
    from .config import get_settings
    from .database import drop_database

    config = get_settings()

    if yes or typer.confirm(
        f"Are you sure you want to drop '{config.database_hostname}:{config.database_name}' ?"
    ):
        drop_database(
            None,
            config.database_name,
        )
        typer.secho("Success.", fg=typer.colors.GREEN)


@database_app.command("upgrade", help="Upgrades database schema to newest version.")
def database_upgrade(
    revision: Annotated[str, typer.Argument(help="Revision identifier.")] = "head",
    dry_run: Annotated[bool, typer.Option(help="Show SQL or execute it.")] = False,
) -> Callable[[str, bool], None]:
    raise typer.Exit()


@database_app.command("heads", help="Shows the heads of the database.")
def database_head() -> None:
    from alembic.command import heads
    from alembic.config import Config as AlembicConfig

    from .config import get_settings

    config = get_settings()
    alembic_cfg = AlembicConfig(str(config.alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(config.alembic_revision_path))
    heads(alembic_cfg)


@database_app.command("history", help="Shows the history of the database.")
def database_history() -> None:
    from alembic.command import history
    from alembic.config import Config as AlembicConfig

    from .config import get_settings

    config = get_settings()
    alembic_cfg = AlembicConfig(str(config.alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(config.alembic_revision_path))
    history(alembic_cfg)


@server_app.command("config", help="Prints the current config")
def server_config() -> None:
    from .config import get_settings

    typer.secho(get_settings().model_dump(), fg=typer.colors.BLUE)


def entrypoint() -> None:
    from .exceptions import AsterException

    try:
        app()
    except AsterException as exc:
        typer.secho(f"ERROR: {exc}", bold=True, fg=typer.colors.RED)
