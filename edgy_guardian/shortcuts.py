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
    return await get_permission_model().query.has_user_perm(user, perm, obj)


async def has_group_permission(user: type[edgy.Model], perm: str, obj: Any) -> bool:
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
        >>> has_permission = await has_group_permission(user, 'edit', some_object)
        >>> if has_permission:
        >>>     print("User has permission to edit the object.")
        >>> else:
        >>>     print("User does not have permission to edit the object.")
    """
    return await get_groups_model().query.has_group_permission(user, perm, obj)


async def assign_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> None:
    """
    Assign or revoke a permission to/from a group, optionally for specific users and/or an object.

    This asynchronous function assigns a specified permission to a group. It can also optionally assign the
    permission for specific users within the group and/or for a specific object. If the `revoke` parameter is
    set to True, the permission will be revoked from the group. To also revoke the permission from the users
    within the group, set `revoke_users_permissions` to True.

    Args:
        perm (str): The permission to assign or revoke. This should be a string representing the permission codename.
        group (type[edgy.Model]): The group to which the permission will be assigned or from which it will be revoked.
        users (type[edgy.Model] | None, optional): The users within the group for whom the permission will be assigned
            or revoked. Defaults to None.
        obj (Any | None, optional): The object for which the permission is assigned or revoked. Defaults to None.
        revoke (bool, optional): If set to True, the permission will be revoked from the group. Defaults to False.
        revoke_users_permissions (bool, optional): If set to True, the permission will also be revoked from the users
            within the group. Defaults to False.

    Returns:
        None

    Example:
        >>> await assign_group_perm('edit', group, users=[user1, user2], obj=some_object)
        >>> await assign_group_perm('view', group, revoke=True)
        >>> await assign_group_perm('delete', group, revoke=True, revoke_users_permissions=True)
    """
    return await get_groups_model().query.assign_group_perm(
        users=users,
        group=group,
        obj=obj,
        perm=perm,
        revoke=revoke,
        revoke_users_permissions=revoke_users_permissions,
    )


async def assign_perm(perm: str, users: Any, obj: Any | None = None, revoke: bool = False) -> None:
    """
    Assigns or revokes a permission for a user or group on a specific object.

    This function allows you to assign or revoke a specific permission for a user or group.
    If the `obj` parameter is provided, the permission is assigned or revoked for that specific object.
    If `obj` is None, the permission is assigned or revoked globally.

    Args:
        perm (str): The permission to assign or revoke. This should be a string representing the permission name.
        users (Any): The user or group to assign or revoke the permission for. This can be an instance of a User or Group model.
        obj (Any, optional): The object to assign or revoke the permission for. This can be any object for which permissions are managed. Defaults to None, meaning the permission is assigned or revoked globally.
        revoke (bool, optional): If True, the permission will be revoked instead of assigned. Defaults to False.

    Returns:
        None: This function does not return any value.

    Raises:
        ValueError: If the `perm` parameter is not a valid permission.
        TypeError: If `users` is not an instance of User or Group.

    Example:
        # Assign the 'edit' permission to a user for a specific object
        await assign_perm('edit', user_instance, obj=some_object)

        # Revoke the 'delete' permission from a group globally
        await assign_perm('delete', group_instance, revoke=True)
    """
    return await get_permission_model().query.assign_perm(
        users=users,
        obj=obj,
        perm=perm,
        revoke=revoke,
    )
