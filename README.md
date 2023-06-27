# Aster

Project example with Python 3.11, FastAPI, Pydantic 2.0, SQLAlchemy 2.0.

## Features

- Full Docker integration (Docker based).
- Docker Compose deployment.
- Python FastAPI backend.
- Pydantic validation.
- JWT token authentication.
- SQLAlchemy models.
- Alembic migrations.
- Arq worker for async tasks.
- REST backend tests based on Pytest.
- Traefik integration.
- Github Actions for CI, including backend testing.
- Promtail/MinIO/Loki for logs
- Prometheus/Grafana for monitoring

## Installation

### Requirements

- Python 3.11+
- Docker
- Docker Compose 2.0+

> You can use poetry or your favourite tool with requirements.txt to install dependencies

### Installing aster

Clone the repository locally:

```sh
git clone https://github.com/odesen/aster.git
```

Before launching the application, you need to a `.env` configuration file. You can check the [example file](https://github.com/odesen/aster/blob/main/.env.example) or the [Settings part](#settings) in this file.

Then, you can use poetry/your tool to install dependencies and launch the application with the CLI `python -m aster server start aster.api:create_app --factory --no-use-colors --no-access-log` or with the debug mode in VSCode

or

you can use docker-compose.

#### Docker Compose

There are 3 files for compose:

- docker-compose.yml : base configuration
- docker-compose.dev.yml : configuration for local development and expose ports for aster and the database.
- deployments/docker-compose.deploy.yml : example of production deployment with Traefik to serve the project, Promtail/Loki/Grafana/Prometheus to monitor

Extend the first file with the environment you want. Examples:

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up db
docker compose -f docker-compose.yml -f deployments/docker-compose.deploy.yml --env-file .env up
```

## Settings

You have to set up the connection with the database by setting multiple enviroment variables :
- `ASTER_DATABASE_HOSTNAME=localhost`
- `ASTER_DATABASE_CREDENTIAL_USER=aster`
- `ASTER_DATABASE_CREDENTIAL_PASSWORD=aster`
- `ASTER_DATABASE_NAME=aster` (optional)
- `ASTER_DATABASE_PORT=5432` (optional)

## CLI

Aster ships with commands to help execute tasks.

### Database

```
Usage: python -m aster database [OPTIONS] COMMAND [ARGS]...

  Contains all aster database-related commands (init, heads, history, upgrade, drop).

Options:
  --help  Show this message and exit.

Commands:
  drop     Drops all data in database.
  heads    Shows the heads of the database.
  history  Shows the history of the database.
  init     Initializes a new database.
  upgrade  Upgrades database schema to newest version.
```

### Server

```
Usage: python -m aster server [OPTIONS] COMMAND [ARGS]...

  Contains all aster server-related commands (start, config)

Options:
  --help  Show this message and exit.

Commands:
  config  Prints the current config
  start
```
