from __future__ import annotations

import pytest
from contenttypes.models import ContentType
from edgy import settings

pytestmark = pytest.mark.anyio

models = settings.edgy_guardian.registry


async def test_get_for_model(client):
    content_type = await ContentType.query.get_for_model("users")

    assert content_type is not None


async def test_get_for_id(client):
    content_type = await ContentType.query.get_for_id(1)

    assert content_type is not None


async def test_cache(client):
    content_type = await ContentType.query.get_for_id(1)

    assert content_type is not None

    assert ContentType.query._cache is not None

    ContentType.query.clear_cache()

    assert ContentType.query._cache == {}

    content_type = await ContentType.query.get_for_id(1)

    assert content_type is not None
