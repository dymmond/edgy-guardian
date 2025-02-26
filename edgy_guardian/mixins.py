from __future__ import annotations

from typing import Any

from edgy_guardian.shortcuts import (
    assign_group_perm,
    assign_perm,
    has_group_permission,
    has_user_perm,
)


class UserMixin:
    """
    Mixin to add permission methods to User model.

    This mixin can be added as an extension to the User model to provide
    methods for assigning and checking permissions for a user.
    """

    async def has_perm(self, perm: str, obj: Any) -> bool:
        """
        Check if the user has the given permission on the given object.

        This asynchronous method checks whether the user has the specified
        permission for the provided object by querying the permissions model.

        Args:
            perm (str): The permission to check.
            obj (Any): The object to check the permission on.

        Returns:
            bool: True if the user has the permission, False otherwise.

        Example:
            >>> has_permission = await user.has_perm('edit', some_object)
            >>> if has_permission:
            >>>     print("User has permission to edit the object.")
            >>> else:
            >>>     print("User does not have permission to edit the object.")
        """
        return await has_user_perm(self, perm, obj)

    async def assign_perm(self, perm: str, obj: Any | None = None, revoke: bool = False) -> None:
        """
        Assign or revoke the given permission for the user.

        This asynchronous method assigns or revokes a specified permission
        for the user. If the `revoke` parameter is set to True, the permission
        will be revoked.

        Args:
            perm (str): The permission to assign or revoke.
            obj (Any, optional): The object to assign or revoke the permission for. Defaults to None.
            revoke (bool, optional): If True, the permission will be revoked; if False, the permission will be assigned. Defaults to False.

        Returns:
            None

        Example:
            >>> await user.assign_perm('edit', some_object)
            >>> await user.assign_perm('view', revoke=True)
        """
        await assign_perm(perm, self, obj, revoke)

    async def assign_group_perm(
        self,
        perm: str,
        group: Any,
        obj: Any | None = None,
        revoke: bool = False,
        revoke_users_permissions: bool = False,
    ) -> None:
        """
        Assign or revoke the given permission for the user's group.

        This asynchronous method assigns or revokes a specified permission
        for the user's group. If the `revoke` parameter is set to True, the
        permission will be revoked from the group. To also revoke the
        permission from the users within the group, set `revoke_users_permissions`
        to True.

        Args:
            perm (str): The permission to assign or revoke.
            group (Any): The group to assign or revoke the permission for.
            obj (Any, optional): The object to assign or revoke the permission for. Defaults to None.
            revoke (bool, optional): If True, the permission will be revoked; if False, the permission will be assigned. Defaults to False.
            revoke_users_permissions (bool, optional): If True, the permission will also be revoked from the user. Defaults to False.

        Returns:
            None

        Example:
            >>> await user.assign_group_perm('edit', group, some_object)
            >>> await user.assign_group_perm('view', group, revoke=True)
            >>> await user.assign_group_perm('delete', group, revoke=True, revoke_users_permissions=True)
        """
        await assign_group_perm(perm, group, self, obj, revoke, revoke_users_permissions)

    async def has_group_permission(self, perm: str, obj: Any) -> bool:
        """
        Check if the user's group has the given permission on the given object.

        This asynchronous method checks whether the user's group has the
        specified permission for the provided object by querying the
        permissions model.

        Args:
            perm (str): The permission to check.
            obj (Any): The object to check the permission on.

        Returns:
            bool: True if the user's group has the permission, False otherwise.

        Example:
            >>> has_permission = await user.has_group_permission('edit', some_object)
            >>> if has_permission:
            >>>     print("User's group has permission to edit the object.")
            >>> else:
            >>>     print("User's group does not have permission to edit the object.")
        """
        return await has_group_permission(self, perm, obj)
