import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 -- registers every model on Base.metadata before create_all
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app as fastapi_app


def _test_database_url() -> str:
    base, _, db_name = settings.database_url.rpartition("/")
    return f"{base}/{db_name}_test"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(_test_database_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
