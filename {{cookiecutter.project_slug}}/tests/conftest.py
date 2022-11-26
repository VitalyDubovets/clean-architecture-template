import pytest
from httpx import AsyncClient

from infrastructure.ioc.container import Container
from main import create_app


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ]
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
def container():
    container = Container()
    container.init_resources()
    yield container
    container.shutdown_resources()


@pytest.fixture(scope="session")
def fastapi_app(container):
    return create_app(container)


@pytest.fixture()
async def async_test_client(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client