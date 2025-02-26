# UserMixin Documentation

## Overview

The `UserMixin` class is a mixin that adds permission methods to the User model. This mixin provides methods for assigning and checking permissions for a user, making it easier to manage user permissions within your application.

## Methods

### `has_perm`

#### Description

Checks if the user has the given permission on the given object.

#### Signature

```python
async def has_perm(self, perm: str, obj: Any) -> bool:
```

#### Parameters

- `perm` (str): The permission to check.
- `obj` (Any): The object to check the permission on.

#### Returns

- `bool`: True if the user has the permission, False otherwise.

#### Example

```python
has_permission = await user.has_perm('edit', some_object)
if has_permission:
    print("User has permission to edit the object.")
else:
    print("User does not have permission to edit the object.")
```

### `assign_perm`

#### Description

Assigns or revokes the given permission for the user.

#### Signature

```python
async def assign_perm(self, perm: str, obj: Any | None = None, revoke: bool = False) -> None:
```

#### Parameters

- `perm` (str): The permission to assign or revoke.
- `obj` (Any, optional): The object to assign or revoke the permission for. Defaults to None.
- `revoke` (bool, optional): If True, the permission will be revoked; if False, the permission will be assigned. Defaults to False.

#### Returns

- `None`

#### Example

```python
await user.assign_perm('edit', some_object)
await user.assign_perm('view', revoke=True)
```

### `assign_group_perm`

#### Description

Assigns or revokes the given permission for the user's group.

#### Signature

```python
async def assign_group_perm(
    self,
    perm: str,
    group: Any,
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> None:
```

#### Parameters

- `perm` (str): The permission to assign or revoke.
- `group` (Any): The group to assign or revoke the permission for.
- `obj` (Any, optional): The object to assign or revoke the permission for. Defaults to None.
- `revoke` (bool, optional): If True, the permission will be revoked; if False, the permission will be assigned. Defaults to False.
- `revoke_users_permissions` (bool, optional): If True, the permission will also be revoked from the user. Defaults to False.

#### Returns

- `None`

#### Example

```python
await user.assign_group_perm('admin', group, obj, some_object)
await user.assign_group_perm('viewer', group, obj, revoke=True)
await user.assign_group_perm('users', group, obj, revoke=True, revoke_users_permissions=True)
```

### `has_group_permission`

#### Description

Checks if the user's group has the given permission on the given object.

#### Signature

```python
async def has_group_permission(self, perm: str, obj: Any) -> bool:
```

#### Parameters

- `perm` (str): The permission to check.
- `obj` (Any): The object to check the permission on.

#### Returns

- `bool`: True if the user's group has the permission, False otherwise.

#### Example

```python
has_permission = await user.has_group_permission('edit', some_object)
if has_permission:
    print("User's group has permission to edit the object.")
else:
    print("User's group does not have permission to edit the object.")
```

## Usage

To use the `UserMixin`, simply add it as a mixin to your User model. This will provide your User model with the methods for assigning and checking permissions.

```python
class User(edgy.Model, UserMixin):
    # Your user model implementation
    ...
```

With the `UserMixin` added to your User model, you can now easily assign and check permissions for users and their groups.

## Conclusion

The `UserMixin` class provides a convenient way to manage user permissions within your application. By using the methods provided by this mixin, you can easily assign and check permissions for users and their groups, making your application more secure and manageable.
