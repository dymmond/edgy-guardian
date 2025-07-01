from __future__ import annotations

import pytest
from accounts.models import User
from permissions.models import Permission

from tests.factories import ItemFactory, ProductFactory, UserFactory

pytestmark = pytest.mark.anyio


class TestUserMixinPermission:

    async def test_get_object_permissions_of_user(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await user.assign_perm(perm="create", obj=item)
        await user.assign_perm(perm="edit", obj=item)
        await user.assign_perm(perm="delete", obj=item)


        await user.assign_perm(perm="create", obj=product)
        await user.assign_perm(perm="update", obj=product)

        total_permissions = await user.obj_perms(item)
        assert len(total_permissions) == 3

        total_permissions = await user.obj_perms(product)
        assert len(total_permissions) == 2
    async def test_assign_permission_to_user(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await user.assign_perm(perm="create", obj=item)
        await user.assign_perm(perm="create", obj=product)

        total_permissions = await Permission.guardian.count()
        assert total_permissions == 2

    async def test_assign_same_permission_to_users(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        await user.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=item)

        total_users = await User.query.all()

        assert len(total_users) == 2

        perms = await Permission.guardian.all()

        assert len(perms) == 1

        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 2

    async def test_assign_and_remove_permissions_to_users(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user.assign_perm(perm="create", obj=product)
        await user_two.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        total_users = await User.query.all()

        assert len(total_users) == 2

        # Check total perms
        perms = await Permission.guardian.all()

        assert len(perms) == 2

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 2

        # Remove Users
        await user.assign_perm(perm="create", obj=item, revoke=True)
        await user_two.assign_perm(perm="create", obj=product, revoke=True)

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 1

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 1

    async def test_assign_and_remove_permissions_to_users_remove_perm(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user.assign_perm(perm="create", obj=product)
        await user_two.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        total_users = await User.query.all()

        assert len(total_users) == 2

        # Check total perms
        perms = await Permission.guardian.all()

        assert len(perms) == 2

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 2

        # Remove Users
        await user.remove_perm(perm="create", obj=item)
        await user_two.remove_perm(perm="create", obj=product)

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 1

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 1

    async def test_remove_perm(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user.assign_perm(perm="create", obj=product)
        await user_two.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        total_users = await User.query.all()

        assert len(total_users) == 2

        # Check total perms
        perms = await Permission.guardian.all()

        assert len(perms) == 2

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 2

        # Remove Users
        await user.remove_perm(perm="create", obj=item)
        await user_two.remove_perm(perm="create", obj=product)

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 1

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 1

    async def test_user_has_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        # Check if user has permission
        has_permission = await user.has_perm(perm="create", obj=item)

        assert has_permission is True

        has_permission = await user_two.has_perm(perm="create", obj=item)

        assert has_permission is True

        has_permission = await user_two.has_perm(perm="create", obj=product)

        assert has_permission is True

    async def test_user_does_not_have_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        has_permission = await user.has_perm(perm="create", obj=product)

        assert has_permission is False

        has_permission = await user_two.has_perm(perm="create", obj=item)

        assert has_permission is False

    async def test_user_does_not_have_permission_then_it_added_and_it_does(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await user.assign_perm(perm="create", obj=item)
        await user_two.assign_perm(perm="create", obj=product)

        has_permission = await user.has_perm(perm="create", obj=product)

        assert has_permission is False

        has_permission = await user_two.has_perm(perm="create", obj=item)

        assert has_permission is False

        # Add Permissions
        await user.assign_perm(perm="create", obj=product)
        await user_two.assign_perm(perm="create", obj=item)

        has_permission = await user.has_perm(perm="create", obj=product)

        assert has_permission is True

        has_permission = await user_two.has_perm(perm="create", obj=item)

        assert has_permission is True
