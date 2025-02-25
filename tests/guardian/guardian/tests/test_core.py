import pytest
from accounts.models import User
from edgy import Registry
from esmerald.conf import settings
from permissions.models import Permission

from edgy_guardian.shortcuts import assign_perm
from tests.factories import ItemFactory, ProductFactory, UserFactory

models: Registry = settings.registry
pytestmark = pytest.mark.anyio


async def test_assign_permission_to_user():
    user = await UserFactory().build_and_save()
    item = await ItemFactory().build_and_save()
    product = await ProductFactory().build_and_save()

    await assign_perm(perm="create", user_or_group=[user], obj=item)
    await assign_perm(perm="create", user_or_group=[user], obj=product)

    total_permissions = await Permission.query.count()
    assert total_permissions == 2


async def test_assign_same_permission_to_users():
    user = await UserFactory().build_and_save()
    user_two = await UserFactory().build_and_save()
    item = await ItemFactory().build_and_save()

    await assign_perm(perm="create", user_or_group=[user], obj=item)
    await assign_perm(perm="create", user_or_group=[user_two], obj=item)

    total_users = await User.query.all()

    assert len(total_users) == 2

    perms = await Permission.query.all()

    assert len(perms) == 1

    total_users_in_permission = await perms[0].users.all()

    assert len(total_users_in_permission) == 2


async def test_assign_and_remove_permissions_to_users():
    user = await UserFactory().build_and_save()
    user_two = await UserFactory().build_and_save()
    item = await ItemFactory().build_and_save()
    product = await ProductFactory().build_and_save()

    # Add Users
    await assign_perm(perm="create", user_or_group=[user, user_two], obj=item)
    await assign_perm(perm="create", user_or_group=[user, user_two], obj=product)

    total_users = await User.query.all()

    assert len(total_users) == 2

    # Check total perms
    perms = await Permission.query.all()

    assert len(perms) == 2

    # Check total users in permission
    total_users_in_permission = await perms[0].users.all()

    assert len(total_users_in_permission) == 2

    total_users_in_permission = await perms[1].users.all()

    assert len(total_users_in_permission) == 2

    # Remove Users
    await assign_perm(perm="create", user_or_group=[user], obj=item, revoke=True)
    await assign_perm(perm="create", user_or_group=[user_two], obj=product, revoke=True)

    # Check total users in permission
    total_users_in_permission = await perms[0].users.all()

    assert len(total_users_in_permission) == 1

    total_users_in_permission = await perms[1].users.all()

    assert len(total_users_in_permission) == 1
