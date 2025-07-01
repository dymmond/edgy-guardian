from typing import Any, cast

import edgy

from edgy_guardian.content_types.utils import get_content_type
from edgy_guardian.enums import UserGroup
from edgy_guardian.exceptions import GuardianImproperlyConfigured
from edgy_guardian.permissions.exceptions import ObjectNotPersisted
from edgy_guardian.utils import get_groups_model, get_permission_model


class ManagerMixin:
    @property
    def user_field(self) -> str:
        """
        Determines the user field for the model class.

        This property checks if the model class has a 'users' attribute and
        returns the corresponding user field name. It is used to identify the
        user-related field in the model.

        Returns:
            str: The user field name, which is "user" if the model class has a
            'users' attribute.
        """
        return UserGroup.USER.value

    @property
    def group_field(self) -> str:
        """
        Determines the group field for the model class.

        This property checks if the model class has a 'groups' attribute and
        returns the corresponding group field name. It is used to identify the
        group-related field in the model.

        Returns:
            str: The group field name, which is "group" if the model class has a
            'groups' attribute.
        """
        return UserGroup.GROUP.value

    @property
    def permissions_field(self) -> str:
        """
        Determines the permissions field for the model class.

        This property checks if the model class has a 'permissions' attribute and
        returns the corresponding group field name. It is used to identify the
        group-related field in the model.

        Returns:
            str: The group field name, which is "group" if the model class has a
            'permissions' attribute.
        """
        return UserGroup.PERMISSIONS.value

    @property
    def group_model(self) -> type[edgy.Model]:
        """
        Returns the groups model class associated with this manager.

        This property retrieves the model class that handles permissions for the
        managed model. It provides a way to access the permissions model class
        directly.

        Returns:
            type[edgy.Model]: The permissions model class associated with this
            manager.
        """
        return cast(type[edgy.Model], get_groups_model())

    @property
    def permissions_model(self) -> type[edgy.Model]:
        """
        Returns the permissions model class associated with this manager.

        This property retrieves the model class that handles permissions for the
        managed model. It provides a way to access the permissions model class
        directly.

        Returns:
            type[edgy.Model]: The permissions model class associated with this
            manager.
        """
        return cast(type[edgy.Model], get_permission_model())

    def _check_field_exists(
        self, field_name: str, field_type: str, model_class: type[edgy.Model] | None = None
    ) -> None:
        """
        Checks if a specified field exists in the model's permissions.

        This method verifies whether a given field name is present in the
        `permissions_model.meta.fields`. If the field does not exist, it raises
        a `GuardianImproperlyConfigured` exception with a detailed error message.

        Args:
            field_name (str): The name of the field to check.
            permissions_model (Any): The model permissions object that contains
                metadata about the fields.
            field_type (str): The expected type of the field (e.g., 'CharField',
                'IntegerField').

        Raises:
            GuardianImproperlyConfigured: If the specified field does not exist
                in the model's permissions.

        Example:
            >>> self._check_field_exists('username', permissions_model, 'CharField')
            GuardianImproperlyConfigured: You are trying to assign a permission to 'username'
            and it does not exist. Edgy Guardian expects a field named 'username' on the
            'UserPermissions' model as 'CharField'.
        """

        if field_name not in model_class.meta.fields:
            raise GuardianImproperlyConfigured(
                f"You are trying to assign a permission to '{field_name}' and it does not exist. "
                f"Edgy Guardian expects a field named '{field_name}' on the '{model_class.__name__}' model as '{field_type}'."
            )


class PermissionManager(edgy.Manager, ManagerMixin):
    @property
    def model(self) -> type[edgy.Model]:
        """
        Returns the model class associated with this manager.

        This property retrieves the model class that is managed by this manager
        instance. It provides a way to access the model class directly.

        Returns:
            type[edgy.Model]: The model class associated with this manager.
        """
        return cast(type[edgy.Model], self.model_class)

    async def assign_perm(
        self,
        perm: type[edgy.Model] | str,
        users: list[edgy.Model] | edgy.Model,
        obj: Any,
        revoke: bool,
    ) -> type[edgy.Model]:
        """
        Assigns or revokes a permission to a user or group for a specific object.
        Args:
            perm (str): The permission to assign or revoke.
            users (list[edgy.Model] | edgy.Model): The user or group to which the permission is assigned or revoked.
            obj (Any): The object for which the permission is assigned or revoked.
            revoke (bool): If True, the permission will be revoked; if False, the permission will be assigned.
        Returns:
            type[edgy.Model]: The permission object that was assigned or revoked.
        Raises:
            GuardianImproperlyConfigured: If the user or group field does not exist or is not a ManyToManyField.
            ObjectNotPersisted: If the object is not persisted.
        """
        self._check_field_exists(self.user_field, "ManyToManyField", self.permissions_model)

        if not isinstance(
            self.permissions_model.meta.fields[self.user_field], edgy.ManyToManyField
        ):
            raise GuardianImproperlyConfigured(
                f"'{self.user_field}' must be a '{edgy.ManyToManyField.__name__}'."
            )

        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first" % obj)

        ctype = await get_content_type(obj)
        if not isinstance(perm, self.permissions_model):
            permission, _ = await self.get_or_create(
                content_type=ctype, codename=perm.lower(), name=perm.capitalize()
            )
        else:
            permission = perm  # type: ignore

        kwargs = {
            "users": users,
            "revoke": revoke,
            "permission": permission,
        }
        await self.permissions_model.assign_permission(**kwargs)
        return cast(type[edgy.Model], permission)

    async def assign_bulk_perm(
        self,
        perms: list[edgy.Model] | list[str],
        users: list[edgy.Model] | edgy.Model,
        objs: list[Any],
        revoke: bool,
    ) -> None:
        """
        Assigns permissions in bulk to a user or list of users.
        """
        self._check_field_exists(self.user_field, "ManyToManyField", self.permissions_model)

        if not isinstance(
            self.permissions_model.meta.fields[self.user_field], edgy.ManyToManyField
        ):
            raise GuardianImproperlyConfigured(
                f"'{self.user_field}' must be a '{edgy.ManyToManyField.__name__}'."
            )

        if not isinstance(perms, list):
            perms = [perms]  # type: ignore

        if not isinstance(users, list):
            users = [users]

        if not isinstance(objs, list):
            objs = [objs]  # type: ignore

        # Pre-fetch content types for all objects to avoid multiple await calls
        content_types = [await get_content_type(obj) for obj in objs]

        # Bulk create objects
        permissions: list[dict[str, Any]] = [
            {"content_type": content_type, "codename": perm.lower(), "name": perm.capitalize()}
            for content_type in content_types
            for perm in perms
        ]

        # Bulk inserts or creates the permissions and internally Edgy does in an atomic way
        permissions = await self.permissions_model.guardian.bulk_get_or_create(
            permissions, unique_fields=["content_type", "codename"]
        )

        # Make sure we add all permissions to the filter
        for perm in permissions:
            self.permissions_model.guardian.filter(
                codename=perm.codename, content_type=perm.content_type
            )

        # Get all permissions that were created
        permissions = await self.permissions_model.guardian.all()

        # Assign permissions in bulk
        kwargs = {
            "users": users,
            "permissions": permissions,
            "revoke": revoke,
        }
        await self.permissions_model.assign_bulk_permission(**kwargs)

    async def has_user_perm(
        self, user: edgy.Model, perm: str | type[edgy.Model], obj: Any
    ) -> bool:
        """
        Checks if user has any permissions for given object.
        """
        return cast(
            bool,
            await self.permissions_model.guardian.has_permission(user=user, perm=perm, obj=obj),
        )

    async def get_obj_perms(self, user: edgy.Model, obj: type[edgy.Model], **filters: Any) -> list[type[edgy.Model]]:
        """
        Return all permission instances of this type that `user` has on `obj`.

        Args:
            user (edgy.Model): the user whose permissions we’re querying.
            obj (edgy.Model): the object to check permissions against.
            **filters: extra lookup args (e.g. codename__iexact="change_stuff").

        Returns:
            List[BasePermission]: all matching permission records.
        """
        return cast(list[type[edgy.Model]], await self.permissions_model.guardian.get_user_obj_perms(user, obj, **filters))

class GroupManager(edgy.Manager, ManagerMixin):
    def __check_many_to_many_field(self, model: type[edgy.Model], field_name: str) -> None:
        """
        Checks if the specified field in the given model is a ManyToManyField.

        Args:
            model: The model to check the field in.
            field_name (str): The name of the field to check.

        Raises:
            GuardianImproperlyConfigured: If the specified field is not a ManyToManyField.
        """
        field_type = model.meta.fields.get(field_name)
        if not isinstance(field_type, edgy.ManyToManyField):
            raise GuardianImproperlyConfigured(
                f"'{field_name}' must be a '{edgy.ManyToManyField.__name__}' in '{model.__name__}'."
            )

    async def assign_group_perm(
        self,
        users: list[edgy.Model] | edgy.Model,
        group: type[edgy.Model] | str,
        obj: Any,
        perm: type[edgy.Model] | str,
        revoke: bool,
        revoke_users_permissions: bool,
    ) -> type[edgy.Model]:
        """
        Assigns or revokes a permission to a user or group for a specific object.
        Args:
            perm (str): The permission to assign or revoke.
            users (list[edgy.Model] | edgy.Model): The user or group to which the permission is assigned or revoked.
            obj (Any): The object for which the permission is assigned or revoked.
            revoke (bool): If True, the permission will be revoked; if False, the permission will be assigned.
        Returns:
            type[edgy.Model]: The permission object that was assigned or revoked.
        Raises:
            GuardianImproperlyConfigured: If the user or group field does not exist or is not a ManyToManyField.
            ObjectNotPersisted: If the object is not persisted.
        """
        self._check_field_exists(self.user_field, "ManyToManyField", self.group_model)
        self._check_field_exists(self.permissions_field, "ManyToManyField", self.group_model)

        # Check if the user field is a ManyToManyField in the group model
        self.__check_many_to_many_field(self.group_model, self.user_field)

        # Check if the permissions field is a ManyToManyField in the group model
        self.__check_many_to_many_field(self.group_model, self.permissions_field)

        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first" % obj)

        # Handles the content type for permissions assignment
        ctype = await get_content_type(obj)
        if not isinstance(perm, self.permissions_model):
            permission, _ = await self.permissions_model.guardian.get_or_create(
                content_type=ctype, codename=perm.lower(), name=perm.capitalize()
            )
        else:
            permission = perm  # type: ignore

        group_kwargs = {
            "permission": permission,
            "users": users,
            "revoke": revoke,
            "group": group,
        }

        # Handles the content type for group assignment
        group_obj = await self.group_model.assign_group_perm(**group_kwargs)

        kwargs = {
            "users": users,
            "permission": permission,
            "revoke": revoke_users_permissions,
        }
        await self.permissions_model.assign_permission(**kwargs)
        return cast(type[edgy.Model], group_obj)

    async def assign_bulk_group_perm(
        self,
        perms: type[edgy.Model] | list[edgy.Model] | list[str],
        users: list[edgy.Model] | edgy.Model,
        groups: list[type[edgy.Model]] | list[str],
        objs: list[Any],
        revoke: bool,
        revoke_users_permissions: bool,
    ) -> None:
        self._check_field_exists(self.user_field, "ManyToManyField", self.group_model)
        self._check_field_exists(self.permissions_field, "ManyToManyField", self.group_model)

        # Check if the user field is a ManyToManyField in the group model
        self.__check_many_to_many_field(self.group_model, self.user_field)

        # Check if the permissions field is a ManyToManyField in the group model
        self.__check_many_to_many_field(self.group_model, self.permissions_field)

        if any(getattr(obj, "pk", None) is None for obj in objs):
            raise ObjectNotPersisted("All objects need to be persisted first")

        if not isinstance(perms, list):
            perms = [perms]  # type: ignore

        if not isinstance(groups, list):
            groups = [groups]  # type: ignore

        if not isinstance(users, list):
            users = [users]

        permissions: list[edgy.Model] = []

        # Pre-fetch content types for all objects to avoid multiple await calls
        content_types = [await get_content_type(obj) for obj in objs]

        # Bulk create objects
        permissions: list[dict[str, Any]] = [  # type: ignore
            {"content_type": content_type, "codename": perm.lower(), "name": perm.capitalize()}
            for content_type in content_types
            for perm in perms  # type: ignore
        ]

        # Bulk inserts or creates the permissions and internally Edgy does in an atomic way
        permissions = await self.permissions_model.guardian.bulk_get_or_create(
            permissions, unique_fields=["content_type", "codename"]
        )

        # Make sure we add all permissions to the filter
        for perm in permissions:
            self.permissions_model.guardian.filter(
                codename=perm.codename, content_type=perm.content_type
            )

        # Get all permissions that were created
        permissions = await self.permissions_model.guardian.all()

        group_kwargs = {
            "perms": permissions,
            "users": users,
            "groups": groups,
            "revoke": revoke,
        }

        # Handles the content type for group assignment
        await self.group_model.assign_bulk_group_perm(**group_kwargs)

        # Handles the permissions
        kwargs = {
            "users": users,
            "permissions": permissions,
            "revoke": revoke_users_permissions,
        }
        await self.permissions_model.assign_bulk_permission(**kwargs)
