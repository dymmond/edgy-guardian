from typing import Any

import edgy

from edgy_guardian.utils import get_groups_model, get_user_model

User = get_user_model()
Group = get_groups_model()


class ObjectPermissionChecker:
    def __init__(self, user_or_group: Any) -> None:
        self.user_or_group = user_or_group
        self._obj_perms_cache: dict[str, Any] = {}


def get_identity(identity: Any) -> tuple[edgy.Model, bool | None]:
    if isinstance(identity, edgy.Manager):
        identity_model_type = identity.model_class
        if identity_model_type == get_user_model():
            return identity, False
        elif identity_model_type == get_groups_model():
            return identity, True

    if isinstance(identity, list) and isinstance(identity[0], User):
        return identity, None

    if isinstance(identity, list) and isinstance(identity[0], Group):
        return None, identity

    if isinstance(identity, get_user_model()):
        return identity, None
    if isinstance(identity, Group):
        return None, identity
