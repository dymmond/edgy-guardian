from typing import Any

from edgy_guardian.utils import get_groups_model, get_permission_model, get_user_model

User = get_user_model()
Group = get_groups_model()
Permission = get_permission_model()


async def assign_perm(
    perm: str, user_or_group: Any, obj: Any | None = None, revoke: bool = False
) -> None:
    """
    Assigns a permission to a user or group.

    Args:
        perm (str): The permission to assign.
        user_or_group (User | Group): The user or group to assign the permission to.
        obj (Any, optional): The object to assign the permission for. Defaults to None.
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
    Bulk Assigns a permission to a user or group.

    Args:
        perm (str): The permission to assign.
        user_or_group (User | Group): The user or group to assign the permission to.
        obj (Any, optional): The object to assign the permission for. Defaults to None.
    """
    return await Permission.assign_permission(
        users=user_or_group,
        obj=obj,
        names=perms,
        bulk_create_or_update=True,
        revoke=revoke,
    )
