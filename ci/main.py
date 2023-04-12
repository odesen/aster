import sys

import anyio
import dagger


async def main() -> None:
    config = dagger.Config(log_output=sys.stdout)

    # initialize Dagger client
    async with dagger.Connection(config) as client:
        database = (
            client.container()
            .from_("postgres:15")
            .with_env_variable("POSTGRES_PASSWORD", "postgres")
            .with_exec(["postgres"])
            .with_exposed_port(5432)
        )
        # use a python:3.11-slim container
        # get version
        pytest = (
            client.container()
            .from_("python:3.11-slim")
            .with_service_binding("db", database)
            .with_env_variable("ASTER_DATABASE_HOSTNAME", "db")
            .with_env_variable("ASTER_DATABASE_CREDENTIAL_USER", "postgres")
            .with_env_variable("ASTER_DATABASE_CREDENTIAL_PASSWORD", "postgres")
            .with_directory("/src", client.host().directory(".", exclude=[".*"]))
            .with_workdir("/src")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "libpq-dev", "gcc", "curl"])
            .with_exec(
                [
                    "curl",
                    "-sSL",
                    "https://install.python-poetry.org",
                    "|",
                    "python3",
                    "-",
                ]
            )
            .with_exec(["poetry", "config", "virtualenvs.in-project", "true"])
            .with_exec(["poetry", "install"])
            .with_exec(["make", "test"])
        )

        # execute
        results = await pytest.stdout()

    # print output
    print(f"{results}")


if __name__ == "__main__":
    anyio.run(main)
