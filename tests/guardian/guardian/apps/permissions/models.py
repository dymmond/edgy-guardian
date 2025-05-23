from __future__ import annotations

import edgy
from esmerald.conf import settings

from edgy_guardian.permissions.models import BaseGroup, BasePermission


class Group(BaseGroup):
    users: list[edgy.Model] = edgy.ManyToManyField(  # type: ignore
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="groups"
    )
    permissions: list[BasePermission] = edgy.ManyToManyField(  # type: ignore
        "Permission",
        through_tablename=edgy.NEW_M2M_NAMING,
        related_name="groups",
    )

    class Meta:
        registry = settings.registry


class Permission(BasePermission):
    users: list[edgy.Model] = edgy.ManyToManyField(  # type: ignore
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="permissions"
    )

    class Meta:
        registry = settings.registry
