from typing import TYPE_CHECKING, ClassVar

import edgy
from core.models import BaseModel
from permissions.managers import GroupManager, PermissionManager

if TYPE_CHECKING:
    from contenttypes.models import ContentType


class Permission(BaseModel):
    """
    A model representing a permission.

    Attributes:
        name (str): The name of the permission.
        codename (str): A unique code name for the permission.
    Methods:
        natural_key() -> tuple[str]:
            Returns the natural key for the permission, which is the codename.
        __str__() -> str:
            Returns the string representation of the permission, which is the name.
    """

    name: str = edgy.CharField(max_length=100)
    content_type: "ContentType" = edgy.ForeignKey("ContentType", on_delete=edgy.CASCADE)
    codename: str = edgy.CharField(max_length=100)

    objects: ClassVar[edgy.Manager] = PermissionManager()

    class Meta:
        unique_together = [("content_type", "codename")]

    def natural_key(self) -> tuple[str]:
        return (self.codename,) + self.content_type.natural_key()

    def __str__(self) -> str:
        return f"{self.content_type} | {self.name}"


class Group(BaseModel):
    """
    Represents a group of permissions.

    Attributes:
        name (CharField): The name of the group, which must be unique and have a maximum length of 100 characters.
        permissions (ManyToManyField): A many-to-many relationship to the Permission model.
    Methods:
        natural_key() -> tuple[str]: Returns a tuple containing the name of the group.
        __str__() -> str: Returns the name of the group as its string representation.
    """

    name: str = edgy.CharField(max_length=100, unique=True)
    permissions: list[Permission] = edgy.ManyToManyField(  # type: ignore
        Permission,
        through_tablename=edgy.NEW_M2M_NAMING,
    )

    objects: ClassVar[edgy.Manager] = GroupManager()

    def natural_key(self) -> tuple[str]:
        return (self.name,)

    def __str__(self) -> str:
        return self.name


class BaseObjectPermission(BaseModel):
    """
    BaseObjectPermission is an abstract base model that defines a foreign key relationship
    to the Permission model. This class is intended to be inherited by other models that
    require object-level permissions.

    Attributes:
        permission (ForeignKey): A foreign key to the Permission model, with a cascade
                                 delete behavior.
    """

    permission: Permission = edgy.ForeignKey("Permission", on_delete=edgy.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        value = str(getattr(self, "user", False) or self.group)
        return f"{value}", {str(self.permission.codename)}


class UserObjectPermissionBase(BaseObjectPermission):
    user = edgy.ForeignKey("User", on_delete=edgy.CASCADE)

    # objects = UserObjectPermissionManager()

    class Meta:
        abstract = True


class UserObjectPermission(UserObjectPermissionBase):
    class Meta:
        unique_together = ["user", "permission"]


class GroupObjectPermissionBase(BaseObjectPermission):
    group = edgy.ForeignKey(Group, on_delete=edgy.CASCADE)

    # objects = GroupObjectPermissionManager()

    class Meta:
        abstract = True


class GroupObjectPermission(GroupObjectPermissionBase):
    class Meta:
        unique_together = ["group", "permission"]
