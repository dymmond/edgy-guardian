from functools import lru_cache

import edgy


@lru_cache
def get_content_type_model() -> edgy.Model:
    """
    Returns the content type model class.

    Returns:
        type[edgy.Model]: The content type model class.
    """
    from edgy.conf import settings

    model = settings.edgy_guardian.content_type_model
    db_model = settings.edgy_guardian.registry.models[model]
    return db_model


@lru_cache
def get_user_model() -> edgy.Model:
    """
    Returns the user model class.

    Returns:
        type[edgy.Model]: The user model class.
    """
    from edgy.conf import settings

    model = settings.edgy_guardian.user_model
    db_model = settings.edgy_guardian.registry.models[model]
    return db_model


@lru_cache
def get_permission_model() -> edgy.Model:
    """
    Returns the permission model class.

    Returns:
        type[edgy.Model]: The permission model class.
    """
    from edgy.conf import settings

    model = settings.edgy_guardian.permission_model
    db_model = settings.edgy_guardian.registry.models[model]
    return db_model


@lru_cache
def get_groups_model() -> edgy.Model:
    """
    Returns the group model class.

    Returns:
        type[edgy.Model]: The group model class.
    """
    from edgy.conf import settings

    model = settings.edgy_guardian.group_model
    db_model = settings.edgy_guardian.registry.models[model]
    return db_model


def get_obj_perms_model(
    obj: edgy.Model, base_cls: edgy.Model, generic_cls: edgy.Model
) -> edgy.Model:
    """
    Returns the object permissions model class.

    Args:
        obj (edgy.Model): The object for which the permissions are managed.
        base_model (edgy.Model): The base model class.
        model (edgy.Model): The model class.

    Returns:
        type[edgy.Model]: The object permissions model class.
    """
    return generic_cls


def get_user_obj_perms_model(obj: edgy.Model) -> edgy.Model:
    """
    Returns the user groups model class.

    Returns:
        type[edgy.Model]: The user groups model class.
    """
    from edgy_guardian.permissions.models import UserObjectPermission, UserObjectPermissionBase

    return get_obj_perms_model(obj, UserObjectPermissionBase, UserObjectPermission)


def get_group_obj_perms_model(obj=None):
    """
    Returns model class that connects given `obj` and Group class.
    If obj is not specified, then group generic object permission model
    returned is determined byt the guardian setting 'GROUP_OBJ_PERMS_MODEL'.
    """
    from edgy_guardian.permissions.models import GroupObjectPermission, GroupObjectPermissionBase

    return get_obj_perms_model(obj, GroupObjectPermissionBase, GroupObjectPermission)
