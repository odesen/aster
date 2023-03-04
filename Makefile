GIT_REVISION = `git rev-parse HEAD`

.PHONY install
install:
	poetry install

.PHONY start
start:
	poetry run uvicorn aster.api:create_app --factory

.PHONY init-database
init-database:
	poetry run python -m aster database init

.PHONY drop-database
reset-database:
	poetry run python -m aster database reset

.PHONY format
format:
	poetry run black

.PHONY lint
lint:
	poetry run ruff

.PHONY test
test:
	poetry run pytest
