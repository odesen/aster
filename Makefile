.ONESHELL:

SHELL := /bin/bash

GIT_REVISION = `git rev-parse HEAD`
DOCKER_IMAGE = "$(USER)/$(shell basename $(CURDIR))"
VERSION := $(shell python -c 'import tomli; print(tomlib.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])')

# .PHONY = install start start-database init-database reset-database format lint test

# clean up

.PHONY: clean
clean: clean-docker clean-pyc clean-test

clean-docker:
	docker rmi $(DOCKER_IMAGE)

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .ruff_cache


# builds and installation


install:
	poetry install

build-image:
	docker build -f Dockerfile --no-cache -t $(DOCKER_IMAGE):$(VERSION) .

build-cached-image:
	docker build -f Dockerfile -t $(DOCKER_IMAGE):$(VERSION) .

# bootstrap

start:
	poetry run uvicorn aster.api:create_app --factory

start-database:
	docker compose -f deployments/docker-compose.yml --env-file .env up db

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
