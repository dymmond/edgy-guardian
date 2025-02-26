import pytest
from contenttypes.models import ContentType
from edgy import Registry, settings
from edgy.conf import settings as edgy_settings

from edgy_guardian.loader import handle_content_types

pytestmark = pytest.mark.anyio

models = settings.edgy_guardian.registry


async def test_handle_content_types_generate_content_types(client):
    total = await ContentType.query.all()

    assert len(total) == len(models.models)

    await handle_content_types()

    total = await ContentType.query.all()

    assert len(total) == len(models.models)


async def test_handle_content_types_when_tables_are_removed_from_registry(client):
    new_registry = Registry(database=models.database)
    new_registry.models = {
        k: v for k, v in models.models.items() if k == "User" or k == "ContentType"
    }
    edgy_settings.edgy_guardian.register(new_registry)

    await handle_content_types()

    total = await ContentType.query.all()

    assert len(total) == 2

    # Rollback to original registry
    edgy_settings.edgy_guardian.register(models)
