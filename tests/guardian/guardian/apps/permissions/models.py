import edgy
from esmerald.conf import settings

from edgy_guardian.permissions.models import Group as BaseGroup, Permission as BasePermission


class BaseModel(edgy.Model):
    class Meta:
        registy = settings.registry


class Group(BaseModel, BaseGroup):
    class Meta:
        registry = settings.registry


class Permission(BaseModel, BasePermission):
    class Meta:
        registry = settings.registry
