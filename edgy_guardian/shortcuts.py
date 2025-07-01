from typing import Any, cast

import edgy
from edgy.exceptions import RelationshipNotFound

from edgy_guardian.utils import get_groups_model, get_permission_model

__all__ = [
    "has_user_perm",
    "has_group_permission",
    "assign_group_perm",
    "assign_bulk_group_perm",
    "assign_perm",
    "remove_perm",
    "remove_group_perm",
    "assign_bulk_perm",
    "remove_bulk_perm",
    "remove_bulk_group_perm",
]


async def get_obj_perms(user: type[edgy.Model], obj: Any, **filters: Any) -> list[type[edgy.Model]]:
    """
    Return all permission instances of this type that `user` has on `obj`.

    Args:
        user (edgy.Model): the user whose permissions we’re querying.
        obj (edgy.Model): the object to check permissions against.
        **filters: extra lookup args (e.g. codename__iexact="change_stuff").

    Returns:
        List[BasePermission]: all matching permission records.
    """
    return cast(list[type[edgy.Model]], await get_permission_model().guardian.get_obj_perms(user, obj, **filters))


async def has_user_perm(user: type[edgy.Model], perm: str | type[edgy.Model], obj: Any) -> bool:
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
    return cast(bool, await get_permission_model().guardian.has_user_perm(user, perm, obj))


async def has_group_permission(
    user: type[edgy.Model], perm: str | type[edgy.Model], group: type[edgy.Model] | str
) -> bool:
    """
    Checks if a user has a specific permission for a given object.

    This asynchronous function verifies whether the specified user has the
    given permission for the provided object by querying the permissions
    model.

    Args:
        user (type[edgy.Model]): The user for whom the permission check is
            being performed.
        perm (str): The permission string to check (e.g., 'view', 'edit').
        group (type[edgy.Model] | str): The object or string for which the group is being checked.

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
    return cast(bool, await get_groups_model().guardian.has_group_permission(user, perm, group))


async def assign_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> Any:
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
    return await get_groups_model().guardian.assign_group_perm(
        users=users,
        group=group,
        obj=obj,
        perm=perm,
        revoke=revoke,
        revoke_users_permissions=revoke_users_permissions,
    )


async def assign_bulk_group_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    groups: list[type[edgy.Model]] | list[str],
    objs: list[Any],
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> Any:
    """
    Assigns or revokes bulk group permissions for users on specified objects.

    This function allows for the bulk assignment or revocation of group permissions for a list of users on a list of objects.
    It can handle both permission models and permission names, as well as single or multiple user models and group models.

    Args:
        perms (list[edgy.Model] | list[str]): A list of permission models or permission names to be assigned or revoked.
            - If a list of permission models is provided, each model should be an instance of the edgy.Model class.
            - If a list of permission names is provided, each name should be a string representing the permission.
        users (list[edgy.Model] | edgy.Model): A list of user models or a single user model to whom the permissions will be assigned or revoked.
            - If a list is provided, each element should be an instance of the edgy.Model class representing a user.
            - If a single user model is provided, it should be an instance of the edgy.Model class.
        groups (list[type[edgy.Model]] | list[str]): A group model or a string representing the group to which the permissions will be assigned or revoked.
            - If a group model is provided, it should be an instance of the edgy.Model class.
            - If a string is provided, it should represent the name of the group.
        objs (list[Any]): A list of objects on which the permissions will be assigned or revoked.
            - Each object in the list can be of any type, depending on the context in which the permissions are being assigned.
        revoke (bool, optional): A flag indicating whether to revoke the specified permissions.
            - If True, the specified permissions will be revoked from the users on the objects.
            - If False (default), the specified permissions will be assigned to the users on the objects.
        revoke_users_permissions (bool, optional): A flag indicating whether to revoke the users' individual permissions when revoking group permissions.
            - If True, the users' individual permissions will also be revoked when revoking group permissions.
            - If False (default), only the group permissions will be revoked.

    Returns:
        Any: The result of the `assign_bulk_group_perm` method from the groups model's guardian.

    Example:
        # Assign group permissions to multiple users on multiple objects
        await assign_bulk_group_perm(
            perms=["read", "write"],
            users=[user1, user2],
            groups="admin",
            objs=[obj1, obj2],
            revoke=False
        )

        # Revoke group permissions from a single user on multiple objects
        await assign_bulk_group_perm(
            perms=["read", "write"],
            users=user1,
            groups="admin",
            objs=[obj1, obj2],
            revoke=True,
            revoke_users_permissions=True
        )
    """
    return await get_groups_model().guardian.assign_bulk_group_perm(
        perms=perms,
        users=users,
        groups=groups,
        objs=objs,
        revoke=revoke,
        revoke_users_permissions=revoke_users_permissions,
    )


async def assign_perm(
    perm: type[edgy.Model] | str, users: Any, obj: Any, revoke: bool = False
) -> Any:
    """
    Assigns or revokes a permission for a user or group on a specific object.

    This function allows you to assign or revoke a specific permission for a user or group.
    If the `obj` parameter is provided, the permission is assigned or revoked for that specific object.
    If `obj` is None, the permission is assigned or revoked globally.

    Args:
        perm (type[edgy.Model] | str): The permission to assign or revoke. This should be a string representing the permission name.
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
    return await get_permission_model().guardian.assign_perm(
        users=users,
        obj=obj,
        perm=perm,
        revoke=revoke,
    )


async def remove_perm(perm: type[edgy.Model] | str, users: Any, obj: Any | None = None) -> None:
    """
    Removes a permission from a user or group for a specific object.

    This asynchronous function revokes a specified permission from a user or group.
    If the `obj` parameter is provided, the permission is revoked for that specific object.
    If `obj` is None, the permission is revoked globally.

    Args:
        perm (type[edgy.Model] | str): The permission to revoke. This should be a string representing the permission name or a permission model instance.
        users (Any): The user or group from whom the permission will be revoked. This can be an instance of a User or Group model.
        obj (Any, optional): The object for which the permission is being revoked. This can be any object for which permissions are managed. Defaults to None, meaning the permission is revoked globally.

    Returns:
        None: This function does not return any value.

    Example:
        # Revoke the 'edit' permission from a user for a specific object
        await remove_perm('edit', user_instance, obj=some_object)

        # Revoke the 'delete' permission from a group globally
        await remove_perm('delete', group_instance)
    """
    try:
        await assign_perm(perm, users, obj, revoke=True)
    except RelationshipNotFound:
        return None


async def remove_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke_users_permissions: bool = False,
) -> None:
    """
    Removes a permission from a group.

    This asynchronous function revokes a specified permission from a group.
    It can also optionally revoke the permission for specific users within the group
    and/or for a specific object. If the `revoke_users_permissions` parameter is set to True,
    the permission will also be revoked from the users within the group.

    Args:
        perm (type[edgy.Model] | str): The permission to revoke. This should be a string representing the permission name or a permission model instance.
        group (type[edgy.Model] | str): The group from which the permission will be revoked. This can be an instance of the group model or the name of the group.
        users (type[edgy.Model] | None, optional): The users within the group for whom the permission will be revoked. Defaults to None.
        obj (Any | None, optional): The object for which the permission is being revoked. Defaults to None.
        revoke_users_permissions (bool, optional): If set to True, the permission will also be revoked from the users within the group. Defaults to False.

    Returns:
        None: This function does not return any value.

    Example:
        # Revoke the 'edit' permission from a group
        await remove_group_perm('edit', group_instance)

        # Revoke the 'view' permission from a group and also from the users within the group
        await remove_group_perm('view', group_instance, revoke_users_permissions=True)
    """
    try:
        await assign_group_perm(
            perm=perm,
            group=group,
            users=users,
            obj=obj,
            revoke=True,
            revoke_users_permissions=revoke_users_permissions,
        )
    except RelationshipNotFound:
        return


async def assign_bulk_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    objs: list[Any],
    revoke: bool = False,
) -> None:
    """
    Assigns or revokes bulk permissions for users on specified objects.

    This function allows for the bulk assignment or revocation of permissions for a list of users on a list of objects.
    It can handle both permission models and permission names, as well as single or multiple user models.

    Args:
        perms (list[edgy.Model] | list[str]): A list of permission models or permission names to be assigned or revoked.
            - If a list of permission models is provided, each model should be an instance of the edgy.Model class.
            - If a list of permission names is provided, each name should be a string representing the permission.
        users (list[edgy.Model] | edgy.Model): A list of user models or a single user model to whom the permissions will be assigned or revoked.
            - If a list is provided, each element should be an instance of the edgy.Model class representing a user.
            - If a single user model is provided, it should be an instance of the edgy.Model class.
        objs (list[Any]): A list of objects on which the permissions will be assigned or revoked.
            - Each object in the list can be of any type, depending on the context in which the permissions are being assigned.
        revoke (bool, optional): A flag indicating whether to revoke the specified permissions.
            - If True, the specified permissions will be revoked from the users on the objects.
            - If False (default), the specified permissions will be assigned to the users on the objects.

    Returns:
        None: This function does not return any value.

    Example:
        # Assign permissions to multiple users on multiple objects
        await assign_bulk_perm(
            perms=["read", "write"],
            users=[user1, user2],
            objs=[obj1, obj2],
            revoke=False
        )

        # Revoke permissions from a single user on multiple objects
        await assign_bulk_perm(
            perms=["read", "write"],
            users=user1,
            objs=[obj1, obj2],
            revoke=True
        )
    """
    await get_permission_model().guardian.assign_bulk_perm(
        users=users,
        objs=objs,
        perms=perms,
        revoke=revoke,
    )


async def remove_bulk_perm(
    perms: list[edgy.Model] | list[str], users: list[edgy.Model] | edgy.Model, objs: list[Any]
) -> None:
    """
    Removes bulk permissions for users on specified objects.

    This function allows for the bulk removal of permissions for a list of users on a list of objects.
    It can handle both permission models and permission names, as well as single or multiple user models.

    Args:
        perms (list[edgy.Model] | list[str]): A list of permission models or permission names to be removed.
            - If a list of permission models is provided, each model should be an instance of the edgy.Model class.
            - If a list of permission names is provided, each name should be a string representing the permission.
        users (list[edgy.Model] | edgy.Model): A list of user models or a single user model from whom the permissions will be removed.
            - If a list is provided, each element should be an instance of the edgy.Model class representing a user.
            - If a single user model is provided, it should be an instance of the edgy.Model class.
        objs (list[Any]): A list of objects from which the permissions will be removed.
            - Each object in the list can be of any type, depending on the context in which the permissions are being removed.

    Returns:
        None: This function does not return any value.

    Raises:
        RelationshipNotFound: If the relationship between the user and the object is not found.

    Example:
        # Remove permissions from multiple users on multiple objects
        await remove_bulk_perm(
            perms=["read", "write"],
            users=[user1, user2],
            objs=[obj1, obj2]
        )

        # Remove permissions from a single user on multiple objects
        await remove_bulk_perm(
            perms=["read", "write"],
            users=user1,
            objs=[obj1, obj2]
        )
    """
    try:
        await assign_bulk_perm(perms, users, objs, revoke=True)
    except RelationshipNotFound:
        return


async def remove_bulk_group_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    groups: list[type[edgy.Model]] | list[str],
    objs: list[Any],
    revoke_users_permissions: bool = False,
) -> None:
    """
    Removes bulk group permissions for users on specified objects.

    This function allows for the bulk removal of group permissions for a list of users on a list of objects.
    It can handle both permission models and permission names, as well as single or multiple user models and group models.

    Args:
        perms (list[edgy.Model] | list[str]): A list of permission models or permission names to be removed.
            - If a list of permission models is provided, each model should be an instance of the edgy.Model class.
            - If a list of permission names is provided, each name should be a string representing the permission.
        users (list[edgy.Model] | edgy.Model): A list of user models or a single user model from whom the permissions will be removed.
            - If a list is provided, each element should be an instance of the edgy.Model class representing a user.
            - If a single user model is provided, it should be an instance of the edgy.Model class.
        groups (type[edgy.Model] | list[str]): A group model or a list of group names from which the permissions will be removed.
            - If a group model is provided, it should be an instance of the edgy.Model class.
            - If a list of strings is provided, each string should represent the name of a group.
        objs (list[Any]): A list of objects from which the permissions will be removed.
            - Each object in the list can be of any type, depending on the context in which the permissions are being removed.
        revoke_users_permissions (bool, optional): A flag indicating whether to revoke the users' individual permissions when revoking group permissions.
            - If True, the users' individual permissions will also be revoked when revoking group permissions.
            - If False (default), only the group permissions will be revoked.

    Returns:
        None: This function does not return any value.

    Raises:
        RelationshipNotFound: If the relationship between the user and the object is not found.

    Example:
        # Remove group permissions from multiple users on multiple objects
        await remove_bulk_group_perm(
            perms=["read", "write"],
            users=[user1, user2],
            groups=["admin", "editor"],
            objs=[obj1, obj2],
            revoke_users_permissions=True
        )

        # Remove group permissions from a single user on multiple objects
        await remove_bulk_group_perm(
            perms=["read", "write"],
            users=user1,
            groups="admin",
            objs=[obj1, obj2],
            revoke_users_permissions=False
        )
    """
    try:
        await assign_bulk_group_perm(
            perms=perms,
            users=users,
            groups=groups,
            objs=objs,
            revoke=True,
            revoke_users_permissions=revoke_users_permissions,
        )
    except RelationshipNotFound:
        return
