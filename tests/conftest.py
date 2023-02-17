import os
from typing import Any, Iterable

import pytest
from fastapi.testclient import TestClient

from aster.api import create_app
from aster.database import drop_database, engine, init_database

pytestmark = pytest.mark.anyio

os.environ["ASTER_DATABASE_NAME"] = "aster-test"


@pytest.fixture(scope="session")
async def database() -> Any:
    await init_database(engine)
    yield
    drop_database(str(engine.url), "aster-test")


@pytest.fixture(scope="session")
def client() -> Iterable[TestClient]:
    yield TestClient(create_app())
