from functools import lru_cache

import edgy
from edgy.conf import settings


@lru_cache
def get_content_type_model() -> edgy.Model:
    """
    Returns the content type model class.

    Returns:
        type[edgy.Model]: The content type model class.
    """
    return settings.edgy_guardian.content_type_model


@lru_cache
def get_user_model() -> edgy.Model:
    """
    Returns the user model class.

    Returns:
        type[edgy.Model]: The user model class.
    """
    return settings.edgy_guardian.user_model


@lru_cache
def get_permission_model() -> edgy.Model:
    """
    Returns the permission model class.

    Returns:
        type[edgy.Model]: The permission model class.
    """
    return settings.edgy_guardian.permission_model


@lru_cache
def get_groups_model() -> edgy.Model:
    """
    Returns the group model class.

    Returns:
        type[edgy.Model]: The group model class.
    """
    return settings.edgy_guardian.group_model
