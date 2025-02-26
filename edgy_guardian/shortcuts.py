from __future__ import annotations

from typing import Any

import edgy

from edgy_guardian.utils import get_groups_model, get_permission_model


async def has_user_perm(user: type[edgy.Model], perm: str, obj: Any) -> bool:
    """
    Checks if a user has a specific permission for a given object.

    This asynchronous function verifies whether the specified user has the
    given permission for the provided object by querying the permissions
    model.

    Args:
        user (type[edgy.Model]): The user for whom the permission check is
            being performed.
        perm (str): The permission string to check (e.g., 'view', 'edit').
        obj (Any): The object for which the permission is being checked.

    Returns:
        bool: True if the user has the specified permission for the object,
        False otherwise.

    Example:
        >>> has_permission = await has_user_perm(user, 'edit', some_object)
        >>> if has_permission:
        >>>     print("User has permission to edit the object.")
        >>> else:
        >>>     print("User does not have permission to edit the object.")
    """
    return await get_groups_model().query.has_user_perm(user, perm, obj)


async def assign_perm_with_group(
    perm: str,
    user: type[edgy.Model],
    group: type[edgy.Model],
    obj: Any | None = None,
    revoke: bool = False,
) -> None:
    """
    Assign a permission to a user within a specific group, optionally for a specific object.

    This function is an asynchronous operation that assigns a specified permission to a user within a given group.

    It can also optionally assign the permission for a specific object.
        perm (str): The permission to assign. This should be a string representing the permission codename.
        user (type[edgy.Model]): The user to whom the permission will be assigned. This should be an instance of the user model.
        group (type[edgy.Model]): The group within which the permission will be assigned. This should be an instance of the group model.

    Args:
        perm (str): The permission to assign.
        user (type[edgy.Model]): The user to whom the permission will be assigned.
        group (type[edgy.Model]): The group within which the permission will be assigned.
        obj (Any | None, optional): The object for which the permission is assigned. Defaults to None.
    Returns:
        None
    """
    return await get_permission_model().query.assign_perm_with_group(
        user=user, group=group, obj=obj, perm=perm, revoke=revoke
    )


async def assign_perm(
    perm: str, user_or_group: Any, obj: Any | None = None, revoke: bool = False
) -> None:
    """
    Assigns or revokes a permission for a user or group on a specific object.

    This function allows you to assign or revoke a specific permission for a user or group.
    If the `obj` parameter is provided, the permission is assigned or revoked for that specific object.
    If `obj` is None, the permission is assigned or revoked globally.

    Args:
        perm (str): The permission to assign or revoke. This should be a string representing the permission name.
        user_or_group (Any): The user or group to assign or revoke the permission for. This can be an instance of a User or Group model.
        obj (Any, optional): The object to assign or revoke the permission for. This can be any object for which permissions are managed. Defaults to None, meaning the permission is assigned or revoked globally.
        revoke (bool, optional): If True, the permission will be revoked instead of assigned. Defaults to False.

    Returns:
        None: This function does not return any value.

    Raises:
        ValueError: If the `perm` parameter is not a valid permission.
        TypeError: If `user_or_group` is not an instance of User or Group.

    Example:
        # Assign the 'edit' permission to a user for a specific object
        await assign_perm('edit', user_instance, obj=some_object)

        # Revoke the 'delete' permission from a group globally
        await assign_perm('delete', group_instance, revoke=True)
    """
    return await get_permission_model().query.assign_perm(
        user_or_group=user_or_group,
        obj=obj,
        perm=perm,
        revoke=revoke,
    )


async def bulk_assign_perm(
    perms: list[str], user_or_group: Any, obj: Any | None = None, revoke: bool = False
) -> None:
    """
    Bulk assigns or revokes permissions for a user or group on a specific object.

    This function allows you to assign or revoke multiple permissions for a user or group in bulk.
    If the `obj` parameter is provided, the permissions are assigned or revoked for that specific object.
    If `obj` is None, the permissions are assigned or revoked globally.

    Args:
        perms (list[str]): A list of permissions to assign or revoke. Each permission should be a string representing the permission name.
        user_or_group (Any): The user or group to assign or revoke the permissions for. This can be an instance of a User or Group model.
        obj (Any, optional): The object to assign or revoke the permissions for. This can be any object for which permissions are managed. Defaults to None, meaning the permissions are assigned or revoked globally.
        revoke (bool, optional): If True, the permissions will be revoked instead of assigned. Defaults to False.

    Returns:
        None: This function does not return any value.

    Raises:
        ValueError: If any of the permissions in `perms` are not valid.
        TypeError: If `user_or_group` is not an instance of User or Group.

    Example:
        # Assign multiple permissions to a user for a specific object
        await bulk_assign_perm(['edit', 'view'], user_instance, obj=some_object)

        # Revoke multiple permissions from a group globally
        await bulk_assign_perm(['delete', 'create'], group_instance, revoke=True)
    """
    return await get_permission_model().query.assign_perm(
        users=user_or_group,
        obj=obj,
        names=perms,
        bulk_create_or_update=True,
        revoke=revoke,
    )
