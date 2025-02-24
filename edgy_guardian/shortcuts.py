from functools import lru_cache
from typing import TYPE_CHECKING, Any

from edgy_guardian.utils import (
    get_content_type_model,
    get_groups_model,
    get_permission_model,
    get_user_model,
)

if TYPE_CHECKING:
    from edgy_guardian.content_types.models import ContentType as BaseContentType

User = get_user_model()
Group = get_groups_model()
ContentType = get_content_type_model()
Permission = get_permission_model()


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
    return await Permission.assign_permission(
        users=user_or_group,
        obj=obj,
        name=perm,
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
    return await Permission.assign_permission(
        users=user_or_group,
        obj=obj,
        names=perms,
        bulk_create_or_update=True,
        revoke=revoke,
    )


@lru_cache
async def _get_content_type_cached(app_label: str, codename: str) -> "BaseContentType":
    """
    Retrieves and caches the content type for a given app label and codename.

    This function uses an LRU (Least Recently Used) cache to store the content type
    associated with the specified app label and codename. This can help improve
    performance by avoiding repeated database queries for the same content type.

    Args:
        app_label (str): The label of the application to which the content type belongs.
        codename (str): The codename of the content type.

    Returns:
        BaseContentType: The content type instance corresponding to the given app label and codename.

    Raises:
        ContentType.DoesNotExist: If no content type is found for the given app label and codename.

    Example:
        # Retrieve and cache the content type for the 'auth' app and 'user' model
        content_type = await _get_content_type_cached('auth', 'user')
    """
    return await ContentType.query.get(app_label=app_label, model=codename)
