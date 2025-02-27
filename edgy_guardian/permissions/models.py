from __future__ import annotations

import logging
from typing import Any, ClassVar

import edgy
from sqlalchemy.exc import IntegrityError

from edgy_guardian.content_types.utils import get_content_type
from edgy_guardian.enums import UserGroup
from edgy_guardian.permissions.managers import (
    GroupManager,
    PermissionManager,
)
from edgy_guardian.utils import get_groups_model, get_user_model

logger = logging.getLogger(__name__)


class BaseUserGroup(edgy.Model):
    __model_type__: ClassVar[str] = None

    class Meta:
        abstract = True


class BasePermission(BaseUserGroup):
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

    __model_type__: ClassVar[str] = UserGroup.USER.value

    name: str = edgy.CharField(max_length=100, null=True)
    content_type: edgy.Model = edgy.ForeignKey("ContentType", on_delete=edgy.CASCADE)
    codename: str = edgy.CharField(max_length=100)

    query: PermissionManager = PermissionManager()

    class Meta:
        abstract = True
        unique_together = [("content_type", "codename")]

    def __str__(self) -> str:
        return f"{self.content_type} | {self.name}"

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
        cls, users: list[edgy.Model], obj: edgy.Model, revoke: bool
    ) -> None:
        """
        Creates or revokes a permission for the given users and object.
        """
        model = getattr(obj, cls.__model_type__, None)
        if not model:
            logger.error(f"Model '{cls.__model_type__}' not found")
            return

        async def process_users(users, action):
            if isinstance(users, list):
                for user in users:
                    await action(user)
            else:
                await action(users)

        try:
            if revoke:
                await process_users(users, model.remove)
            else:
                await process_users(users, model.add)
        except IntegrityError as e:
            logger.error("Error processing permission", error=str(e))

    @classmethod
    async def assign_permission(
        cls,
        users: list[edgy.Model] | Any,
        permission: "BasePermission",
        revoke: bool = False,
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
        assert isinstance(users, list) or isinstance(users, get_user_model()), (
            "Users must be a list or a User instance."
        )

        if not isinstance(users, list):
            users = [users]

        return await cls.__assign_permission(users, permission, revoke)

    @classmethod
    async def has_permission(cls, user: edgy.Model, perm: str, obj: Any) -> bool:
        """
        Checks if a user has a specific permission on a given object.

        Args:
            user (edgy.Model): The user to check the permission for.
            perm (str): The permission to check.
            obj (Any): The object to check the permission on.
        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        ctype = await get_content_type(obj)
        filter_kwargs = {
            f"{cls.__model_type__}__id__in": [user.id],
            "codename__iexact": perm,
            "content_type": ctype,
        }
        return await cls.query.filter(**filter_kwargs).exists()


class BaseGroup(BaseUserGroup):
    """
    Represents a group of permissions.

    Attributes:
        name (CharField): The name of the group, which must be unique and have a maximum length of 100 characters.
        permissions (ManyToManyField): A many-to-many relationship to the Permission model.
    Methods:
        natural_key() -> tuple[str]: Returns a tuple containing the name of the group.
        __str__() -> str: Returns the name of the group as its string representation.
    """

    __model_type__: ClassVar[str] = UserGroup.GROUP.value

    name: str = edgy.CharField(max_length=100, index=True)
    query: ClassVar[GroupManager] = GroupManager()

    class Meta:
        unique_together = ["name"]
        abstract = True

    def __str__(self) -> str:
        return self.name

    @classmethod
    async def __assign_users(cls, users: list[edgy.Model], obj: edgy.Model, revoke: bool) -> None:
        model = getattr(obj, UserGroup.USER, None)
        if not model:
            logger.error(f"Model '{cls.__model_type__}' not found")
            return

        async def process_users(users, action):
            if isinstance(users, list):
                for user in users:
                    await action(user)
            else:
                await action(users)

        try:
            if revoke:
                await process_users(users, model.remove)
            else:
                await process_users(users, model.add)
        except IntegrityError as e:
            logger.error("Error processing permission", error=str(e))

    @classmethod
    async def assign_group_perm(
        cls,
        users: list[edgy.Model] | edgy.Model,
        permission: type["BasePermission"],
        group: type[edgy.Model] | str,
        revoke: bool = False,
    ) -> None:
        """
        Assign or revoke a permission for a group.

        This asynchronous class method assigns or revokes a specified permission
        for a given group. If the `revoke` parameter is set to True, the
        permission will be revoked from the group.

        Args:
            permission (type["BasePermission"]): The permission to assign or revoke.
            group (type[edgy.Model] | str): The group to which the permission will
                be assigned or from which it will be revoked. This can be an
                instance of the group model or the name of the group.
            revoke (bool, optional): If set to True, the permission will be revoked
                from the group. Defaults to False.

        Returns:
            None

        Raises:
            GuardianImproperlyConfigured: If the group is not an instance of the
                group model and cannot be retrieved or created.

        Example:
            >>> await cls.assign_group_perm(permission, group)
            >>> await cls.assign_group_perm(permission, "admin", revoke=True)
        """
        # Assigns the users
        assert isinstance(users, list) or isinstance(users, get_user_model()), (
            "Users must be a list or a User instance."
        )

        if not isinstance(users, list):
            users = [users]

        # Handles the content type for group assignment
        if not isinstance(group, cls):
            group_obj, _ = await cls.query.get_or_create(name=group)
        else:
            group_obj = group

        # Assign/Revoke the users from the group
        await cls.__assign_users(users, group_obj, revoke)

        # Get the permission object from the group model
        permissions = getattr(group_obj, UserGroup.PERMISSIONS)
        if not revoke:
            await permissions.add(permission)
        else:
            await permissions.remove(permission)

        return group_obj

    @classmethod
    async def has_group_permission(cls, user: edgy.Model, perm: str, obj: Any) -> bool:
        """
        Checks if a user has a specific permission on a given object.

        This asynchronous class method verifies whether the specified user has
        the given permission for the provided object by querying the permissions
        model.

        Args:
            user (edgy.Model): The user to check the permission for.
            perm (str): The permission to check.
            obj (Any): The object to check the permission on.

        Returns:
            bool: True if the user has the specified permission on the object,
            False otherwise.

        Example:
            >>> has_permission = await cls.has_group_permission(user, 'edit', some_object)
            >>> if has_permission:
            >>>     print("User has permission to edit the object.")
            >>> else:
            >>>     print("User does not have permission to edit the object.")
        """
        filter_kwargs = {
            f"{UserGroup.USER}__id__in": [user.id],
            "id": obj.id,
            f"{UserGroup.PERMISSIONS}__codename__iexact": perm,
        }
        return await get_groups_model().query.filter(**filter_kwargs).exists()
