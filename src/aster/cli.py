import asyncio

import click
import uvicorn

import aster


@click.group()
@click.version_option(aster.ASTER_VERSION)
def aster_cli() -> None:
    ...


@aster_cli.group("database")
def aster_database() -> None:
    ...


@aster_database.command("init")
def database_init() -> None:
    from .database import engine, init_database

    click.echo("Initializing new database...")
    asyncio.run(init_database(engine))
    click.secho("Success.", fg="green")


@aster_database.command("drop")
@click.option("--yes", is_flag=True, help="Silences all confirmation prompts.")
def database_drop(yes: bool) -> None:
    from .config import get_settings
    from .database import drop_database

    config = get_settings()

    if yes or click.confirm(
        f"Are you sure you want to drop '{config.database_hostname}:{config.database_name}' ?"
    ):
        drop_database(
            f"postgresql://{config.database_credential_user.get_secret_value()}:{config.database_credential_password.get_secret_value()}@{config.database_hostname}:{config.database_port}",
            config.database_name,
        )
        click.secho("Success.", fg="green")


@aster_database.command("upgrade")
@click.option("--dry-run", is_flag=True, default=False, help="Show SQL or execute it.")
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
def database_upgrade(dry_run: bool, revision: str) -> None:
    ...


@aster_database.command("heads")
def database_head() -> None:
    from alembic.command import heads
    from alembic.config import Config as AlembicConfig

    from .config import get_settings

    config = get_settings()
    alembic_cfg = AlembicConfig(str(config.alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(config.alembic_revision_path))
    heads(alembic_cfg)


@aster_database.command("history")
def database_history() -> None:
    from alembic.command import history
    from alembic.config import Config as AlembicConfig

    from .config import get_settings

    config = get_settings()
    alembic_cfg = AlembicConfig(str(config.alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(config.alembic_revision_path))
    history(alembic_cfg)


@aster_cli.group("server")
def aster_server() -> None:
    ...


@aster_server.command("config")
def server_config() -> None:
    from .config import get_settings

    click.secho(get_settings().dict(), fg="blue")


aster_server.add_command(uvicorn.main, name="start")


def entrypoint() -> None:
    from .exceptions import AsterException

    try:
        aster_cli()
    except AsterException as exc:
        click.secho(f"ERROR: {exc}", bold=True, fg="red")
