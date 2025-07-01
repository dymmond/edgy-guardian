import logging
from typing import Any, ClassVar, cast

import edgy
from sqlalchemy.exc import IntegrityError

from edgy_guardian._internal._models import BaseGuardianModel
from edgy_guardian.content_types.utils import get_content_type
from edgy_guardian.enums import UserGroup
from edgy_guardian.permissions.managers import (
    GroupManager,
    PermissionManager,
)
from edgy_guardian.utils import get_groups_model, get_permission_model, get_user_model

logger = logging.getLogger(__name__)


class BaseUserGroup(BaseGuardianModel):
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
    content_type: edgy.ForeignKey = edgy.ForeignKey("ContentType", on_delete=edgy.CASCADE)
    codename: str = edgy.CharField(max_length=100)

    guardian: ClassVar[Any] = PermissionManager()  # noqa

    class Meta:
        abstract = True
        unique_together = [("content_type", "codename")]

    def __str__(self) -> str:
        return f"{self.content_type} | {self.name}"

    @classmethod
    async def __bulk_create_or_update_permissions(
        cls,
        users: list["edgy.Model"],
        permissions: list["edgy.Model"],
        revoke: bool,
    ) -> None:
        """
        Creates or updates a list of permissions for the given users and objects.

        Args:
            users (list[edgy.Model]): List of user models to update permissions for.
            permissions (list[edgy.Model]): List of permission models to apply.
            revoke (bool): Flag indicating whether to revoke (True) or add (False) permissions.

        Raises:
            AssertionError: If the model type is not found in the permission.
            IntegrityError: If there is an error processing the permission.
        """

        async def process_users(users: list["edgy.Model"] | Any, action: Any) -> None:
            """
            Processes a list of users with the given action.

            Args:
                users (list[edgy.Model]): List of user models to process.
                action (Callable): The action to perform on each user.
            """
            if isinstance(users, list):
                for user in users:
                    await action(user)
            else:
                await action(users)

        for permission in permissions:
            model = getattr(permission, cls.__model_type__, None)
            if not model:
                logger.error(f"Model '{cls.__model_type__}' not found")
                raise AssertionError(f"'{cls.__model_type__}' not found")

            try:
                action = model.remove if revoke else model.add
                await process_users(users, action)
            except IntegrityError as e:
                logger.error("Error processing permission", error=str(e))
                raise e

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

        async def process_users(users: list[Any] | Any, action: Any) -> None:
            if isinstance(users, list):
                for user in users:
                    await action(user)
            else:
                await action(users)

        try:
            action = model.remove if revoke else model.add
            await process_users(users, action)
        except IntegrityError as e:
            logger.error("Error processing permission", error=str(e))
            raise e

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
        assert isinstance(users, list) or isinstance(users, get_user_model()), (  # type: ignore
            "Users must be a list or a User instance."
        )

        if not isinstance(users, list):
            users = [users]

        return await cls.__assign_permission(users, permission, revoke)

    @classmethod
    async def has_permission(cls, user: edgy.Model, perm: str | type["BasePermission"], obj: Any) -> bool:
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
            "codename__iexact": perm if isinstance(perm, str) else perm.codename,
            "content_type": ctype,
        }
        return cast(bool, await cls.guardian.filter(**filter_kwargs).exists())

    @classmethod
    async def get_user_obj_perms(cls, user: edgy.Model, obj: edgy.Model, **filters: Any) -> list[type[edgy.Model]]:
        """
        Return all permission instances of this type that `user` has on `obj`.

        Args:
            user (edgy.Model): the user whose permissions we’re querying.
            obj (edgy.Model): the object to check permissions against.
            **filters: extra lookup args (e.g. codename__iexact="change_stuff").

        Returns:
            List[BasePermission]: all matching permission records.
        """
        ctype = await get_content_type(obj)

        lookup = {
            f"{cls.__model_type__}__id": user.id,
            "content_type": ctype,
            **filters,
        }
        return cast(list[type[edgy.Model]], await cls.guardian.filter(**lookup).all())

    @classmethod
    async def assign_bulk_permission(
        cls,
        users: list["edgy.Model"],
        permissions: list["edgy.Model"],
        revoke: bool = False,
    ) -> None:
        """
        Assign or revoke a list of permissions for a user or a list of users on a given object.

        This method processes a list of users and assigns or revokes the specified permissions
        for each user. It handles both adding and removing permissions based on the `revoke` flag.

        Args:
            users (List[edgy.Model]): A list of user models to whom the permissions will be assigned or revoked.
            permissions (List[edgy.Model]): A list of permission models to be assigned or revoked.
            revoke (bool, optional): If True, the permissions will be revoked. If False, the permissions will be assigned. Defaults to False.

        Raises:
            AssertionError: If the model type is not found in the permission.
            IntegrityError: If there is an error processing the permission.

        Example:
            users = [user1, user2]
            permissions = [perm1, perm2]
            await PermissionManager.assign_bulk_permission(users, permissions, revoke=False)
        """
        assert isinstance(users, list), "Users must be a list."
        assert isinstance(permissions, list), "Permissions must be a list."

        return await cls.__bulk_create_or_update_permissions(users, permissions, revoke)


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
    guardian: ClassVar[Any] = GroupManager()  # noqa

    class Meta:
        unique_together = ["name"]
        abstract = True

    def __str__(self) -> str:
        return self.name

    @classmethod
    async def __assign_users(
        cls, users: list[type[edgy.Model]] | type[edgy.Model], obj: edgy.Model, revoke: bool
    ) -> None:
        model = getattr(obj, UserGroup.USER, None)
        if not model:
            logger.error(f"Model '{cls.__model_type__}' not found")
            return

        async def process_users(users: list[Any] | Any, action: Any) -> None:
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
        users: list[type[edgy.Model]] | type[edgy.Model],
        permission: type["BasePermission"],
        group: type["BaseGroup"] | str,
        revoke: bool = False,
    ) -> Any:
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
        assert isinstance(users, list) or isinstance(users, get_user_model()), (  # type: ignore
            "Users must be a list or a User instance."
        )

        if not isinstance(users, list):
            users = [users]

        # Handles the content type for group assignment
        if isinstance(group, str):
            group_obj, _ = await cls.guardian.get_or_create(name=group.lower())
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
    async def assign_bulk_group_perm(
        cls,
        users: list[type[edgy.Model]] | type[edgy.Model],
        perms: list[type["BasePermission"]] | type["BasePermission"],
        groups: list[str] | list["BaseGroup"],
        revoke: bool = False,
    ) -> None:
        """
        Assign or revoke a list of permissions for a user or a list of users in specified groups.

        This method processes a list of users and assigns or revokes the specified permissions
        for each user within the given groups. It handles both adding and removing permissions
        based on the `revoke` flag.

        Args:
            users (List[edgy.Model]): A list of user models to whom the permissions will be assigned or revoked.
            perms (List[Type[BasePermission]]): A list of permission models to be assigned or revoked.
            groups (List[str]): A list of group names to which the permissions will be applied.
            revoke (bool, optional): If True, the permissions will be revoked. If False, the permissions will be assigned. Defaults to False.

        Raises:
            AssertionError: If users is not a list or a User instance.
            IntegrityError: If there is an error processing the permission.

        Example:
            users = [user1, user2]
            perms = [perm1, perm2]
            groups = ['group1', 'group2']
            await PermissionManager.assign_bulk_group_perm(users, perms, groups, revoke=False)
        """
        assert isinstance(users, list) or isinstance(users, get_user_model()), (  # type: ignore
            f"Users must be a list or a '{get_user_model().__name__}' instance."
        )

        assert isinstance(perms, list) or isinstance(users, get_permission_model()), (  # type: ignore
            f"Permissions must be a list or a '{get_permission_model().__name__}' instance."
        )

        async def process_permissions(permissions: list[Any] | Any, action: Any) -> None:
            if isinstance(permissions, list):
                for permission in permissions:
                    await action(permission)
            else:
                await action(permissions)

        # Pre-fetch group objects to minimize await calls
        group_objs = []
        for group in groups:
            if not isinstance(group, cls):
                group_obj, _ = await cls.guardian.get_or_create(name=group.lower())
            else:
                group_obj = group
            group_objs.append(group_obj)

        for group_obj in group_objs:
            # Assign/Revoke the users from the group
            await cls.__assign_users(users, group_obj, revoke)

            # Get the permission object from the group model
            permissions = getattr(group_obj, UserGroup.PERMISSIONS)

            try:
                action = permissions.remove if revoke else permissions.add
                await process_permissions(perms, action)
            except IntegrityError as e:
                logger.error("Error processing permission", error=str(e))
                raise e

    @classmethod
    async def has_group_permission(
        cls, user: edgy.Model, perm: str | type[edgy.Model], group: type["BaseGroup"] | str
    ) -> bool:
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
            "name": group.name if isinstance(group, cls) else group,
            f"{UserGroup.PERMISSIONS}__codename__iexact": perm.codename
            if isinstance(perm, BasePermission)
            else perm,
        }
        return cast(bool, await get_groups_model().guardian.filter(**filter_kwargs).exists())
