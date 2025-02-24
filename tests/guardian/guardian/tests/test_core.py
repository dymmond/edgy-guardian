import pytest
from edgy import Registry
from esmerald.conf import settings

from edgy_guardian.shortcuts import assign_perm
from tests.factories import ItemFactory, ProductFactory, UserFactory

models: Registry = settings.registry
pytestmark = pytest.mark.anyio


async def test_assign_permission_to_user():
    user = await UserFactory().build_and_save()
    item = await ItemFactory().build_and_save()
    product = await ProductFactory().build_and_save()

    breakpoint()
    await assign_perm(perm="create", user_or_group=[user], obj=item)
    await assign_perm(perm="create", user_or_group=[user], obj=product)
