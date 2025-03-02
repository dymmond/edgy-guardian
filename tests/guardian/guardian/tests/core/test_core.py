from __future__ import annotations

import pytest
from accounts.models import User
from permissions.models import Group, Permission

from edgy_guardian.content_types.utils import get_content_type
from edgy_guardian.shortcuts import (
    assign_bulk_group_perm,
    assign_bulk_perm,
    assign_group_perm,
    assign_perm,
    has_group_permission,
    has_user_perm,
    remove_bulk_group_perm,
    remove_bulk_perm,
    remove_group_perm,
    remove_perm,
)
from tests.factories import ItemFactory, ProductFactory, UserFactory

pytestmark = pytest.mark.anyio


class TestPermission:
    async def test_assign_permission_to_user(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_perm(perm="create", users=[user], obj=item)
        await assign_perm(perm="create", users=[user], obj=product)

        total_permissions = await Permission.guardian.count()
        assert total_permissions == 2

    async def test_assign_same_permission_to_users(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        await assign_perm(perm="create", users=[user], obj=item)
        await assign_perm(perm="create", users=[user_two], obj=item)

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
        await assign_perm(perm="create", users=[user, user_two], obj=item)
        await assign_perm(perm="create", users=[user, user_two], obj=product)

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
        await assign_perm(perm="create", users=[user], obj=item, revoke=True)
        await assign_perm(perm="create", users=[user_two], obj=product, revoke=True)

        # Check total users in permission
        total_users_in_permission = await perms[0].users.all()

        assert len(total_users_in_permission) == 1

        total_users_in_permission = await perms[1].users.all()

        assert len(total_users_in_permission) == 1

    async def test_assign_and_remove_permissions_to_users_with_remove_perm(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Making sure it does not blow if does not exist
        await remove_perm(perm="create", users=[user], obj=item)

        # Add Users
        await assign_perm(perm="create", users=[user, user_two], obj=item)
        await assign_perm(perm="create", users=[user, user_two], obj=product)

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
        await remove_perm(perm="create", users=[user], obj=item)
        await remove_perm(perm="create", users=[user_two], obj=product)

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
        await assign_perm(perm="create", users=[user, user_two], obj=item)
        await assign_perm(perm="create", users=[user, user_two], obj=product)

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
        await remove_perm(perm="create", users=[user], obj=item)
        await remove_perm(perm="create", users=[user_two], obj=product)

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
        await assign_perm(perm="create", users=[user, user_two], obj=item)
        await assign_perm(perm="create", users=[user_two], obj=product)

        # Check if user has permission
        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_user_perm(user=user_two, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_user_perm(user=user_two, perm="create", obj=product)

        assert has_permission is True

        has_permission = await has_user_perm(user=user, perm="create", obj=product)

        assert has_permission is False

    async def test_user_has_permission_obj(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await assign_perm(perm="create", users=[user, user_two], obj=item)
        await assign_perm(perm="create", users=[user_two], obj=product)

        ctpe = await get_content_type(item)
        perm_item = await Permission.guardian.get(codename="create", content_type=ctpe)

        ctp = await get_content_type(product)
        perm_product = await Permission.guardian.get(codename="create", content_type=ctp)

        # Check if user has permission
        has_permission = await has_user_perm(user=user, perm=perm_item, obj=item)

        assert has_permission is True

        has_permission = await has_user_perm(user=user_two, perm=perm_item, obj=item)

        assert has_permission is True

        has_permission = await has_user_perm(user=user_two, perm=perm_product, obj=product)

        assert has_permission is True

        has_permission = await has_user_perm(user=user, perm=perm_product, obj=product)

        assert has_permission is False

    async def test_user_does_not_have_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await assign_perm(perm="create", users=[user], obj=item)
        await assign_perm(perm="create", users=[user_two], obj=product)

        has_permission = await has_user_perm(user=user, perm="create", obj=product)

        assert has_permission is False

        has_permission = await has_user_perm(user=user_two, perm="create", obj=item)

        assert has_permission is False

    async def test_user_does_not_have_permission_then_it_added_and_it_does(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        # Add Users
        await assign_perm(perm="create", users=[user], obj=item)
        await assign_perm(perm="create", users=[user_two], obj=product)

        has_permission = await has_user_perm(user=user, perm="create", obj=product)

        assert has_permission is False

        has_permission = await has_user_perm(user=user_two, perm="create", obj=item)

        assert has_permission is False

        await assign_perm(perm="create", users=[user], obj=product)
        await assign_perm(perm="create", users=[user_two], obj=item)

        has_permission = await has_user_perm(user=user, perm="create", obj=product)

        assert has_permission is True

        has_permission = await has_user_perm(user=user_two, perm="create", obj=item)

        assert has_permission is True

    async def test_remove_user_remove_automatically_from_permissions(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        await assign_perm(perm="create", users=[user], obj=item)

        permission = await Permission.guardian.first()
        total_users_in_permission = await permission.users.all()

        assert len(total_users_in_permission) == 1

        await user.delete()

        permission = await Permission.guardian.first()
        total_users_in_permission = await permission.users.all()

        assert len(total_users_in_permission) == 0


class TestGroupPermissions:
    async def test_assign_group_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        group = await assign_group_perm(
            perm="create", users=[user, user_two], obj=item, group="admin"
        )

        total_groups = await Group.guardian.all()

        assert len(total_groups) == 1

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 2

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 1

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

    async def test_remove_user_removes_automatically_from_groups(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        group = await assign_group_perm(perm="create", users=[user], obj=item, group="admin")

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 1

        await user.delete()

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 0

    async def test_remove_user_from_groups_does_not_remove_from_permission(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        group = await assign_group_perm(perm="create", users=[user], obj=item, group="admin")

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 1

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 1

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 1

        await group.users.remove(user)

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 0

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 1

    async def test_remove_user_from_groups_does_not_remove_using_remove_group_perm(self, client):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        # Making sure it does not blow if does not exist
        await remove_group_perm(perm="create", users=[user], obj=item, group="admin")

        # Add Users
        group = await assign_group_perm(perm="create", users=[user], obj=item, group="admin")

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 1

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 1

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 1

        await remove_group_perm(perm="create", users=[user], obj=item, group="admin")

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 0

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 1

    async def test_remove_user_from_groups_removes_user_from_permissions_remove_group_perm(
        self, client
    ):
        user = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()

        group = await assign_group_perm(perm="create", users=[user], obj=item, group="admin")

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 1

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 1

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 1

        await remove_group_perm(
            perm="create", users=[user], obj=item, group="admin", revoke_users_permissions=True
        )

        total_users_in_group = await group.users.all()

        assert len(total_users_in_group) == 0

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 0

    async def test_user_has_group_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        group = await assign_group_perm(
            perm="create", users=[user, user_two], obj=item, group="admin"
        )

        group2 = await assign_group_perm(perm="create", users=[user], obj=product, group="users")

        has_permission = await has_group_permission(user=user, perm="create", group=group)

        assert has_permission is True

        has_permission = await has_group_permission(user=user_two, perm="create", group=group)

        assert has_permission is True

        has_permission = await has_group_permission(user=user_two, perm="create", group=group2)

        assert has_permission is False


class TestBulkPermission:
    async def test_assign_bulk_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_perm(
            perms=["create", "edit", "delete"],
            users=[user, user_two],
            objs=[item, product],
            revoke=False,
        )

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

    async def test_remove_bulk_permission(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_perm(
            perms=["create", "edit", "delete"],
            users=[user, user_two],
            objs=[item, product],
            revoke=False,
        )

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_user_perm(user=user, perm="edit", obj=item)

        assert has_permission is True

        # Remove the permissions
        await remove_bulk_perm(
            perms=["delete"],
            users=[user, user_two],
            objs=[item, product],
        )

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is False

        has_permission = await has_user_perm(user=user, perm="edit", obj=item)

        assert has_permission is False


class TestBulkGroupPermission:
    async def test_assign_bulk_group_perm(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_group_perm(
            perms=["create", "edit", "delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
        )
        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

    async def test_remove_bulk_group_perm(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()
        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_group_perm(
            perms=["create", "edit", "delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
        )
        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        # Remove the permissions

        await remove_bulk_group_perm(
            perms=["delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
        )

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="create", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="users")

        assert has_permission is False

    async def test_remove_bulk_group_perm_with_revoke_users_permissions(self, client):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()

        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_group_perm(
            perms=["create", "edit", "delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
        )

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        # Remove the permissions

        await remove_bulk_group_perm(
            perms=["delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
            revoke_users_permissions=True,
        )

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="create", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="users")

        assert has_permission is False

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 0

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 0

    async def test_remove_bulk_group_perm_with_revoke_users_permissions_and_revoke_group_permissions(
        client,
    ):
        user = await UserFactory().build_and_save()
        user_two = await UserFactory().build_and_save()

        item = await ItemFactory().build_and_save()
        product = await ProductFactory().build_and_save()

        await assign_bulk_group_perm(
            perms=["create", "edit", "delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
        )

        total_permissions = await Permission.guardian.all()

        assert len(total_permissions) == 6

        total_users_in_permission = await total_permissions[0].users.all()

        assert len(total_users_in_permission) == 2

        total_users_in_permission = await total_permissions[1].users.all()

        assert len(total_users_in_permission) == 2

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is True

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        # Remove the permissions

        await remove_bulk_group_perm(
            perms=["delete"],
            groups=["admin", "users"],
            users=[user, user_two],
            objs=[item, product],
            revoke_users_permissions=True,
        )

        has_permission = await has_user_perm(user=user, perm="create", obj=item)

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="create", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="admin")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="create", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="read", group="users")

        assert has_permission is False

        has_permission = await has_group_permission(user=user, perm="admin", group="users")

        assert has_permission is False
