"""
Generated by 'esmerald createproject' using Esmerald 3.6.0
"""

from typing import AsyncGenerator

import pytest
from edgy import Registry
from esmerald.conf import settings
from esmerald.testclient import EsmeraldTestClient
from httpx import ASGITransport, AsyncClient

from ..main import get_application


def create_app():
    app = get_application()
    return app


def get_client():
    return EsmeraldTestClient(create_app())


@pytest.fixture
def client():
    return get_client()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": False})


@pytest.fixture(autouse=True, scope="function")
async def create_test_database():
    models: Registry = settings.registry
    async with models.database:
        await models.create_all()
        yield
        if not models.database.drop:
            await models.drop_all()


@pytest.fixture(autouse=True, scope="function")
async def rollback_transactions():
    models: Registry = settings.registry
    async with models.database:
        yield


@pytest.fixture()
async def async_client(app) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        # optional if you want to
        # have some time sleep if you are testing for instance, headers that expire after
        # a certain amount of time
        # Uncomment the line below if you want this or remove completely.

        # await to_thread.run_sync(blocking_function)
        yield ac
