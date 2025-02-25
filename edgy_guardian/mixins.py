from __future__ import annotations

from typing import Any

from edgy_guardian.shortcuts import assign_perm, has_user_perm


class UserMixin:
    """
    Mixin to add permission methods to User model.

    This mixin can be added as an extension to the User model to provide
    methods for assigning and checking permissions for a user.
    """

    async def has_perm(self, perm: str, obj: Any) -> bool:
        """
        Check if the user has the given permission on the given object.

        Args:
            perm (str): The permission to check.
            obj (Any): The object to check the permission on.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        return await has_user_perm(self, perm, obj)

    async def assign_perm(self, perm: str, obj: Any | None = None, revoke: bool = False) -> None:
        """
        Assign or revoke the given permission for the user.

        Args:
            perm (str): The permission to assign or revoke.
            obj (Any, optional): The object to assign or revoke the permission for. Defaults to None.
            revoke (bool, optional): If True, the permission will be revoked; if False, the permission will be assigned. Defaults to False.
        """
        await assign_perm(perm, self, obj, revoke)
