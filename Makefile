GIT_REVISION = `git rev-parse HEAD`

# .PHONY = install start start-database init-database reset-database format lint test

# builds and installation

install:
	poetry install

# bootstrap

start:
	poetry run uvicorn aster.api:create_app --factory

start-database:
	docker compose -f docker-compose.yml --env-file .env up db

init-database:
	poetry run python -m aster database init

reset-database:
	poetry run python -m aster database reset

# git hooks

pre-commit:
	pre-commit run --all-files

# code style

format:
	poetry run black

lint:
	poetry run ruff

# test

test:
	poetry run pytest
