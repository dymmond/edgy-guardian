from __future__ import annotations

from typing import Any

import edgy

from edgy_guardian.content_types.utils import get_content_type
from edgy_guardian.enums import UserGroup
from edgy_guardian.exceptions import GuardianImproperlyConfigured
from edgy_guardian.permissions.exceptions import ObjectNotPersisted
from edgy_guardian.utils import get_permission_model


class PermissionManager(edgy.Manager):
    """
    Manager class for handling Permission objects.

    Methods
    -------
    get_by_natural_key(codename: str, app_label: str, model: str) -> "Permission"
        Asynchronously retrieves a Permission object based on its natural key.
    Asynchronously retrieves a Permission object based on its natural key.

    Parameters
    ----------
    codename : str
        The codename of the permission.
    app_label : str
        The app label associated with the permission.
    model : str
        The model associated with the permission.
    Returns
    -------

    Permission
        The Permission object that matches the given natural key.
    """

    @property
    def model(self) -> type[edgy.Model]:
        """
        Returns the model class associated with this manager.

        This property retrieves the model class that is managed by this manager
        instance. It provides a way to access the model class directly.

        Returns:
            type[edgy.Model]: The model class associated with this manager.
        """
        return self.model_class

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
    def model_permissions(self) -> type[edgy.Model]:
        """
        Returns the permissions model class associated with this manager.

        This property retrieves the model class that handles permissions for the
        managed model. It provides a way to access the permissions model class
        directly.

        Returns:
            type[edgy.Model]: The permissions model class associated with this
            manager.
        """
        return get_permission_model()

    async def get_by_natural_key(
        self, codename: str, app_label: str, model: str
    ) -> type[edgy.Model]:
        return await self.get(
            codename=codename,
            content_type__app_label=app_label,
            content_type__model=model,
        )

    def __check_field_exists(self, field_name: str, field_type: str) -> None:
        """
        Checks if a specified field exists in the model's permissions.

        This method verifies whether a given field name is present in the
        `model_permissions.meta.fields`. If the field does not exist, it raises
        a `GuardianImproperlyConfigured` exception with a detailed error message.

        Args:
            field_name (str): The name of the field to check.
            model_permissions (Any): The model permissions object that contains
                metadata about the fields.
            field_type (str): The expected type of the field (e.g., 'CharField',
                'IntegerField').

        Raises:
            GuardianImproperlyConfigured: If the specified field does not exist
                in the model's permissions.

        Example:
            >>> self.__check_field_exists('username', model_permissions, 'CharField')
            GuardianImproperlyConfigured: You are trying to assign a permission to 'username'
            and it does not exist. Edgy Guardian expects a field named 'username' on the
            'UserPermissions' model as 'CharField'.
        """
        if field_name not in self.model_permissions.meta.fields:
            raise GuardianImproperlyConfigured(
                f"You are trying to assign a permission to '{field_name}' and it does not exist. "
                f"Edgy Guardian expects a field named '{field_name}' on the '{self.model_permissions.__name__}' model as '{field_type}'."
            )

    async def assign_perm(
        self, perm: str, user_or_group: list[edgy.Model] | edgy.Model, obj: Any, revoke: bool
    ) -> type[edgy.Model]:
        """
        Assigns or revokes a permission to a user or group for a specific object.
        Args:
            perm (str): The permission to assign or revoke.
            user_or_group (list[edgy.Model] | edgy.Model): The user or group to which the permission is assigned or revoked.
            obj (Any): The object for which the permission is assigned or revoked.
            revoke (bool): If True, the permission will be revoked; if False, the permission will be assigned.
        Returns:
            type[edgy.Model]: The permission object that was assigned or revoked.
        Raises:
            GuardianImproperlyConfigured: If the user or group field does not exist or is not a ManyToManyField.
            ObjectNotPersisted: If the object is not persisted.
        """
        self.__check_field_exists(self.user_field, "ManyToManyField")

        if not isinstance(
            self.model_permissions.meta.fields[self.user_field], edgy.ManyToManyField
        ):
            raise GuardianImproperlyConfigured(
                f"'{self.user_field}' must be a '{edgy.ManyToManyField.__name__}'."
            )

        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first" % obj)

        ctype = await get_content_type(obj)
        if not isinstance(perm, self.model_permissions):
            permission, _ = await self.get_or_create(
                content_type=ctype, codename=perm, name=perm.capitalize()
            )
        else:
            permission = perm

        kwargs = {
            "users": user_or_group,
            "revoke": revoke,
            "permission": permission,
            "user_or_groups": self.user_field,
        }
        obj_perm = await self.model_permissions.assign_permission(**kwargs)
        return obj_perm

    async def has_user_perm(self, user: edgy.Model, perm: str, obj: Any) -> bool:
        """
        Checks if user has any permissions for given object.
        """
        return await self.model_permissions.query.has_permission(user=user, perm=perm, obj=obj)


class GroupManager(PermissionManager):
    """
    Manager class for handling operations related to Group model.

    Methods:
    --------
    get_by_natural_key(name: str) -> Group:
        Asynchronously retrieves a Group instance by its natural key (name).
    """

    async def get_by_natural_key(self, name: str) -> type[edgy.Model]:
        return await self.get(name=name)

    async def assign_perm_with_group(
        self,
        user: edgy.Model,
        group: edgy.Model,
        obj: Any,
        perm: str,
        revoke: bool,
    ) -> type[edgy.Model]:
        """
        Assigns or revokes a permission to a user or group for a specific object.
        Args:
            perm (str): The permission to assign or revoke.
            user_or_group (list[edgy.Model] | edgy.Model): The user or group to which the permission is assigned or revoked.
            obj (Any): The object for which the permission is assigned or revoked.
            revoke (bool): If True, the permission will be revoked; if False, the permission will be assigned.
        Returns:
            type[edgy.Model]: The permission object that was assigned or revoked.
        Raises:
            GuardianImproperlyConfigured: If the user or group field does not exist or is not a ManyToManyField.
            ObjectNotPersisted: If the object is not persisted.
        """
        self.__check_field_exists(self.user_field, "ManyToManyField")
        self.__check_field_exists(self.group_field, "ManyToManyField")
