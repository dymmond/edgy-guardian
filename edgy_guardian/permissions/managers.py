from typing import Any

import edgy

from edgy_guardian.content_types.utils import get_content_type
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

        Returns:
            type[edgy.Model]: The model class.
        """

        return self.model_class

    @property
    def user_or_group_field(self) -> str:
        """
        Determines whether the model class has a 'user' attribute or not.

        Returns:
            str: "user" if the model class has a 'user' attribute, otherwise "group".
        """

        return self.model_class.__model_type__

    @property
    def model_permissions(self) -> type[edgy.Model]:
        """
        Returns the model class associated with this manager.

        Returns:
            type[edgy.Model]: The model class.
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

        if self.user_or_group_field not in self.model_permissions.meta.fields:
            raise GuardianImproperlyConfigured(
                f"You are trying to assign a permission to '{self.user_or_group_field}' and it does not exist. Edgy Guardian expects a field named '{self.user_or_group_field}' on the '{self.model_permissions.__name__}' model as 'ManyToManyField'."
            )
        elif not isinstance(
            self.model_permissions.meta.fields[self.user_or_group_field], edgy.ManyToManyField
        ):
            raise GuardianImproperlyConfigured(
                f"'{self.user_or_group_field}' must be a '{edgy.ManyToManyField.__name__}'."
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
            "user_or_groups": self.user_or_group_field,
        }
        obj_perm = await self.model_permissions.assign_permission(**kwargs)
        return obj_perm

    async def has_user_perm(self, user: edgy.Model, perm: str, obj: Any) -> bool:
        """
        Checks if user has any permissions for given object.
        """
        return await self.model_permissions.query.has_permission(user=user, perm=perm, obj=obj)


class GroupManager(edgy.Manager):
    """
    Manager class for handling operations related to Group model.

    Methods:
    --------
    get_by_natural_key(name: str) -> Group:
        Asynchronously retrieves a Group instance by its natural key (name).
    """

    async def get_by_natural_key(self, name: str) -> type[edgy.Model]:
        return await self.get(name=name)
