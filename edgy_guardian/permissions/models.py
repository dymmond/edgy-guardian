import logging
from typing import Any, ClassVar

import edgy
from sqlalchemy.exc import IntegrityError

from edgy_guardian.permissions.managers import GroupManager, PermissionManager
from edgy_guardian.utils import get_content_type_model, get_user_model

logger = logging.getLogger(__name__)

ContentType = get_content_type_model()
User = get_user_model()


class BasePermission(edgy.Model):
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
    content_type: edgy.Model = edgy.ForeignKey("ContentType", on_delete=edgy.CASCADE)
    codename: str = edgy.CharField(max_length=100)

    query: ClassVar[edgy.Manager] = PermissionManager()

    class Meta:
        unique_together = [("content_type", "codename")]
        abstact = True

    def natural_key(self) -> tuple[str]:
        return (self.codename,) + self.content_type.natural_key()

    def __str__(self) -> str:
        return f"{self.content_type} | {self.name}"


class Permission(BasePermission):
    class Meta:
        tablename = "edgy_guardian_permission"
        unique_together = [("content_type", "codename")]

    @classmethod
    async def __bulk_create_or_update_permissions(
        cls, users: list[edgy.Model], obj: edgy.Model, names: list[str], revoke: bool
    ) -> None:
        """
        Creates or updates a list of permissions for the given users and object.
        """
        if not revoke:
            permissions = [{"users": users, "obj": obj, "name": name} for name in names]
            try:
                return await cls.query.bulk_create(permissions)
            except IntegrityError as e:
                logger.error("Error creating permissions", error=str(e))
            return None

        return await cls.query.filter(users__in=users, obj=obj, name__in=names).delete()

    @classmethod
    async def __assign_permission(
        cls, users: list[edgy.Model], obj: edgy.Model, name: str, revoke: bool
    ) -> None:
        """
        Creates a permission for the given users and object.
        """
        if not revoke:
            try:
                return await cls.query.create(users=users, obj=obj, name=name)
            except IntegrityError as e:
                logger.error("Error creating permission", error=str(e))
            return None

        return await cls.query.filter(users__in=users, obj=obj, name=name).delete()

    @classmethod
    async def assign_permission(
        cls,
        users: list[edgy.Model] | Any,
        obj: edgy.Model,
        name: str | None = None,
        revoke: bool = False,
        bulk_create_or_update: bool = False,
        names: list[str] | None = None,
    ) -> None:
        """
        Assign or revoke permissions for a user or a list of users on a given object.

        Args:
            users (list["User"] | "User"): A user or a list of users to whom the permission will be assigned or revoked.
            obj (edgy.Model): The object on which the permission will be assigned or revoked.
            name (str | None, optional): The name of the permission to be assigned or revoked. Defaults to None.
            revoke (bool, optional): If True, the permission will be revoked. If False, the permission will be assigned. Defaults to False.
            bulk_create_or_update (bool, optional): If True, permissions will be created or updated in bulk. Defaults to False.
            names (list[str] | None, optional): A list of permission names to be created or updated in bulk. Required if bulk_create_or_update is True. Defaults to None.
        Raises:
            AssertionError: If users is not a list or a User instance.
            ValueError: If bulk_create_or_update is True and names is not provided.
        Returns:
            None
        """
        assert isinstance(users, list) or isinstance(users, User), (
            "Users must be a list or a User instance."
        )

        if not isinstance(users, list):
            users = [users]

        if bulk_create_or_update and not names:
            raise ValueError(
                "You must provide a list of names to create or update permissions in bulk.",
            )
        elif bulk_create_or_update:
            return await cls.__bulk_create_or_update_permissions(users, obj, names, revoke)

        return await cls.__assign_permission(users, obj, name, revoke)


class BaseGroup(edgy.Model):
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

    query: ClassVar[edgy.Manager] = GroupManager()

    class Meta:
        abstract = True

    def natural_key(self) -> tuple[str]:
        return (self.name,)

    def __str__(self) -> str:
        return self.name


class Group(BaseGroup):
    class Meta:
        tablename = "edgy_guardian_groups"


class BaseObjectPermission(edgy):
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

    class Meta:
        abstract = True


class UserObjectPermission(UserObjectPermissionBase):
    class Meta:
        unique_together = ["user", "permission"]


class GroupObjectPermissionBase(BaseObjectPermission):
    group = edgy.ForeignKey(Group, on_delete=edgy.CASCADE)

    class Meta:
        abstract = True


class GroupObjectPermission(GroupObjectPermissionBase):
    class Meta:
        unique_together = ["group", "permission"]
