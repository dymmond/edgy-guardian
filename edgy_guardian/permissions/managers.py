from typing import Any

import edgy

from edgy_guardian.contenttypes.utils import get_content_type
from edgy_guardian.permissions.exceptions import ObjectNotPersisted
from edgy_guardian.utils import get_groups_model, get_permission_model

Group = get_groups_model()
Permission = get_permission_model()


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

    async def get_by_natural_key(
        self, codename: str, app_label: str, model: str
    ) -> type[edgy.Model]:
        return await self.get(
            codename=codename,
            content_type__app_label=app_label,
            content_type__model=model,
        )


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


class BaseObjectPermissionManager(edgy.Manager):
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

        try:
            self.model_class.user  # noqa
            return "user"
        except AttributeError:
            return "group"

    async def assign_perm(self, perm: str, user_or_group: str, obj: Any) -> type[edgy.Model]:
        """
        Assigns permission with given `perm` for an instance `obj` and
        `user`.
        """
        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first" % obj)
        ctype = await get_content_type(obj)
        if not isinstance(perm, Permission):
            permission = Permission.query.get(content_type=ctype, codename=perm)
        else:
            permission = perm

        kwargs = {"permission": permission, self.user_or_group_field: user_or_group}
        obj_perm, _ = await self.get_or_create(**kwargs)
        return obj_perm

    # def bulk_assign_perm(self, perm: str, user_or_group: str, queryset: edgy.QuerySet) -> Any:
    #     """
    #     Bulk assigns permissions with given `perm` for an objects in `queryset` and
    #     `user_or_group`.
    #     """
    #     if isinstance(queryset, list):
    #         ctype = get_content_type(queryset[0])
    #     else:
    #         ctype = get_content_type(queryset.model_class)

    #     if not isinstance(perm, Permission):
    #         permission = Permission.query.get(content_type=ctype, codename=perm)
    #     else:
    #         permission = perm

    #     checker = ObjectPermissionChecker(user_or_group)

    #     assigned_perms = []
    #     for instance in queryset:
    #         if not checker.has_perm(permission.codename, instance):
    #             kwargs = {"permission": permission, self.user_or_group_field: user_or_group}
    #             kwargs["content_object"] = instance
    #             assigned_perms.append(self.model(**kwargs))
    #     self.model.query.bulk_create(assigned_perms)

    #     return assigned_perms
