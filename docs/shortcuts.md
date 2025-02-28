# Shortcuts

## Introduction

In modern applications, managing user permissions is crucial for ensuring security and proper access control. This documentation provides a comprehensive guide on how to use the provided code to manage user permissions, groups, and content types effectively.

### What is a Permission?

A permission is a rule that defines what actions a user or group of users can perform on a specific object or resource within an application. Permissions are typically represented as strings, such as 'view', 'edit', or 'delete'.

### What is a Group?

A group is a collection of users that share common permissions. By assigning permissions to a group, you can manage access control for multiple users simultaneously. This simplifies the process of granting and revoking permissions.

### What is a Content Type?

A content type represents the type of object or resource for which permissions are being managed. For example, in a content management system, content types might include articles, images, and videos. Managing permissions at the content type level allows for fine-grained access control.

## Available shortcuts

Edgy Guardian comes with batteries included, this means, comes with ready to use `shortcuts` to speed up
your development process without thinking too much.

!!! Warning
    If you skiped the [quickstart](index.md#how-to-use-edgy-guardian), now it will be a good time to go there and revisit it.

Assuming that you read the [installation](./index.md) section and understood how you should assemble the Edgy Guardian,
now it is the time to make sure you can use all of those cool functionalities that we want so much.

Whem implementing the `ContentType`, `Permission` and `Group` model, a lot of magic happens behind the scenes and the
purpose of using the library is to simplify your life as much as possible in the long-run development process.

To be able o use the shortcuts, those can be imported from `edgy_guardian.shortcuts`.

### `assign_perm`

Now this one is a beauty. So simple and yet so powerful.

This function allows you, as the name suggests, to assign a permission to a user but also allows you
to revoke it, all in one.

```python
from edgy_guardian.shortcuts import assign_perm
```

#### Signature

```python
async def assign_perm(perm: str, users: Any, obj: Any, revoke: bool = False) -> Any:
```

#### Parameters

- **`perm`**: The permission to assign or revoke. This should be a string representing the permission name.
- **`users`**: The user or group to assign or revoke the permission for. This can be an instance or list of a users.
- **`obj`**: The object to assign or revoke the permission for. This can be any object for which permissions are managed. Defaults to None, meaning the permission is assigned or revoked globally.
- **`revoke`**: If True, the permission will be revoked instead of assigned. Defaults to False.

#### Example

```python
# Assign the 'edit' permission to a user for a specific object
await assign_perm('edit', user_instance, obj=some_object)

# Revoke the 'delete' permission from a user
await assign_perm('delete', user_instance, obj=some_object, revoke=True)
```

### `remove_perm`

This does the exact opposite of the [assign_perm](#assign_perm). Instead of assigning a permission
to a user, it removes it.

```python
from edgy_guardian.shortcuts import remove_perm
```

#### Signature

```python
async def remove_perm(perm: str, users: Any, obj: Any | None = None, revoke: bool = False) -> None:
```

#### Parameters

- **`perm`**: The permission to revoke. This should be a string representing the permission name.
- **`users`**: The user or group to revoke the permission for. This can be an instance or list of a users.
- **`obj`**: The object to revoke the permission for. This can be any object for which permissions are managed. 

#### Example

```python
await remove_perm('edit', user_instance, obj=some_object)
```

This can be also achieved with [assign_perm](#assign_perm) by passing the `revoke=True` flag.

```python
await assign_perm('delete', user_instance, obj=some_object, revoke=True)
```

### `assign_group_perm`

Assign or revoke a permission to/from a group, optionally for specific users and/or an object.

This asynchronous function assigns a specified permission to a group. It can also optionally assign the
permission for specific users within the group and/or for a specific object. 

If the `revoke` parameter is set to True, the permission will be revoked from the group.

To also revoke the permission from the users within the group, set `revoke_users_permissions` to True.

```python
from edgy_guardian.shortcuts import assign_group_perm
```

#### Signature

```python
async def assign_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> Any:
```

#### Parameters

- **`perm`**: The permission to assign or revoke. This should be a string representing the permission codename.
- **`group`**: The group to which the permission will be assigned or from which it will be revoked.
- **`users`**: The users within the group for whom the permission will be assigned or revoked. Defaults to None.
- **`obj`**: The object for which the permission is assigned or revoked. Defaults to None.
- **`revoke`**: If set to True, the permission will be revoked from the group. Defaults to False.
- **`revoke_users_permissions`**: If set to True, the permission will also be revoked from the users within the group. Defaults to False.

#### Example

```python
await assign_group_perm('edit', group, users=[user1, user2], obj=some_object)
await assign_group_perm('view', group, revoke=True)
await assign_group_perm('delete', group, revoke=True, revoke_users_permissions=True)
```

### `remove_group_perm`

This does the opposite of [assign_group_perm](#assign_group_perm) which means, removes a permission from a group.

This asynchronous function revokes a specified permission from a group. It can also optionally revoke the permission for specific users within the group
and/or for a specific object. If the `revoke_users_permissions` parameter is set to True, 
the permission will also be revoked from the users within the group.

#### Signature

```python
async def remove_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke_users_permissions: bool = False,
) -> None:
```

#### Parameters

- **`perm`**: The permission to assign or revoke. This should be a string representing the permission codename.
- **`group`**: The group to which the permission will be assigned or from which it will be revoked.
- **`users`**: The users within the group for whom the permission will be assigned or revoked. Defaults to None.
- **`obj`**: The object for which the permission is assigned or revoked. Defaults to None.
- **`revoke_users_permissions`**: If set to True, the permission will also be revoked from the users within the group. Defaults to False.

#### Example

```python
await remove_group_perm('edit', group, users=[user1, user2], obj=some_object)
await remove_group_perm('view', group, users=[user2], obj=some_object)
await remove_group_perm('delete', group, revoke=True, revoke_users_permissions=True)
```

### `assign_bulk_perm`

Assigns or revokes bulk permissions for users on specified objects.

This function allows for the bulk assignment or revocation of permissions for a list of users on a list of objects.
It can handle both permission models and permission names, as well as single or multiple user models.

#### Signature

```python
async def assign_bulk_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    objs: list[Any],
    revoke: bool = False,
) -> None:
```

#### Parameters

- **`perms`**: A list of permission models or permission names to be assigned or revoked.
- **`users`**: A list of user models or a single user model to whom the permissions will be assigned or revoked.
- **`objs`**: A list of objects on which the permissions will be assigned or revoked.
- **`revoke`**: A flag indicating whether to revoke the specified permissions.

#### Example

```python
await assign_bulk_perm(
    perms=["create", "edit", "delete"],
    users=[user, user_two],
    objs=[item, product],
)

await assign_bulk_perm(
    perms=["create", "edit", "delete"],
    users=[user, user_two],
    objs=[item, product],
    revoke=True,
)
```

### `remove_bulk_perm`

Removes bulk permissions for users on specified objects.

This function allows for the bulk removal of permissions for a list of users on a list of objects.
It can handle both permission models and permission names, as well as single or multiple user models.

#### Signature

```python
async def remove_bulk_perm(
    perms=["create", "edit", "delete"],
    users=[user, user_two],
    objs=[item, product],
) -> None:
```

#### Parameters

- **`perms`**: A list of permission models or permission names to be assigned or revoked.
- **`users`**: A list of user models or a single user model to whom the permissions will be assigned or revoked.
- **`objs`**: A list of objects on which the permissions will be assigned or revoked.

#### Example

```python
await remove_bulk_perm(
    perms=["create", "edit", "delete"],
    users=[user, user_two],
    objs=[item, product],
)
```

### `assign_bulk_group_perm`

Assigns or revokes bulk permissions for users on specified objects.

This function allows for the bulk assignment or revocation of permissions for a list of users on a list of objects.
It can handle both permission models and permission names, as well as single or multiple user models.

#### Signature

```python
async def assign_bulk_group_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    groups: type[edgy.Model] | list[str],
    objs: list[Any],
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> Any:
```

#### Parameters

- **`perms`**: A list of permission models or permission names to be assigned or revoked.
- **`users`**: A list of user models or a single user model to whom the group permissions will be assigned or revoked.
- **`groups`**: A list of group models or a list of strings representing the groups to which the permissions will be assigned or revokeded.
- **`objs`**: A list of objects on which the permissions will be assigned or revoked.
- **`revoke`**: A flag indicating whether to revoke the specified group permissions.
- **`revoke_users_permissions`**: A flag indicating whether to revoke the users' individual permissions when revoking group permissions.

#### Example

```python
await assign_bulk_group_perm(
    perms=["create", "edit", "delete"],
    groups=["admin", "users"],
    users=[user, user_two],
    objs=[item, product],
)

# Revoke group permissions
await assign_bulk_group_perm(
    perms=["create", "edit", "delete"],
    groups=["admin", "users"],
    users=[user, user_two],
    objs=[item, product],
    revoke=True
)

# Revoke user permissions
await assign_bulk_group_perm(
    perms=["create", "edit", "delete"],
    groups=["admin", "users"],
    users=[user, user_two],
    objs=[item, product],
    revoke=True,
    revoke_users_permissions=True
)
```

### `remove_bulk_group_perm`

Removes bulk group permissions for users on specified objects.

This function allows for the bulk removal of group permissions for a list of users on a list of objects.
It can handle both permission models and permission names, as well as single or multiple user models and group models.

#### Signature

```python
async def remove_bulk_group_perm(
    perms: list[edgy.Model] | list[str],
    users: list[edgy.Model] | edgy.Model,
    groups: type[edgy.Model] | list[str],
    objs: list[Any],
    revoke_users_permissions: bool = False,
) -> Any:
```

#### Parameters

- **`perms`**: A list of permission models or permission names to be assigned or revoked.
- **`users`**: A list of user models or a single user model to whom the group permissions will be assigned or revoked.
- **`groups`**: A list of group models or a list of strings representing the groups to which the permissions will be assigned or revokeded.
- **`objs`**: A list of objects on which the permissions will be assigned or revoked.
- **`revoke_users_permissions`**: A flag indicating whether to revoke the users' individual permissions when revoking group permissions.

#### Example

```python
await remove_bulk_group_perm(
    perms=["delete"],
    groups=["admin", "users"],
    users=[user, user_two],
    objs=[item, product],
)


# Revoke user permissions
await remove_bulk_group_perm(
    perms=["delete"],
    groups=["admin", "users"],
    users=[user, user_two],
    objs=[item, product],
    revoke_users_permissions=True
)
```

### `has_user_perm`

This is another out of the box functionality that can be very handy to check if a `user` has a specific permission for a given object.

This asynchronous function verifies whether the specified user has the given permission for the provided object by querying the permissions
model.

```python
from edgy_guardian.shortcuts import has_user_perm
```

#### Signature

```python
async def has_user_perm(user: type[edgy.Model], perm: str, obj: Any) -> bool:
```

#### Parameters

- **`user`**: The user for whom the permission check is being performed.
- **`perm`**: The permission string to check (E.g.: 'view', 'edit').
- **`obj`**: The object for which the permission is being checked.

#### Example

```python
has_permission = await has_user_perm(user, 'edit', some_object)

if has_permission:
    print("User has permission to edit the object.")
else:
    print("User does not have permission to edit the object.")
```

### `has_group_permission`

#### Description

Checks if a user has a specific permission for a given object.

This asynchronous function verifies whether the specified user has the 
given permission for the provided object by querying the permissions model.

#### Signature

```python
async def has_group_permission(user: type[edgy.Model], perm: str, obj: Any) -> bool:
```

#### Parameters

- `user`: The user for whom the permission check is being performed.
- `perm`: The permission string to check (e.g., 'view', 'edit').
- `obj`: The object for which the permission is being checked.

#### Example

```python
has_permission = await has_group_permission(user, 'edit', some_object)

if has_permission:
    print("User has permission to edit the object.")
else:
    print("User does not have permission to edit the object.")
```

## Real-Life Examples

### Example 1: Assigning Permissions to a User

In a content management system, you might want to allow certain users to edit articles. Here's how you can assign the 'edit' permission to a user for a specific article:

```python
article = get_article_by_id(1)
user = get_user_by_id(1)
await assign_perm('edit', user, obj=article)
```

### Example 2: Revoking Permissions from a Group

If you want to revoke the 'delete' permission from a group of users globally, you can do so as follows:

```python
group = get_group_by_name('Editors')
await assign_perm('delete', group, revoke=True)
```

### Example 3: Checking User Permissions

Before allowing a user to perform an action, you might want to check if they have the necessary permissions. For example, to check if a user can edit an article:

```python

article = get_article_by_id(1)
user = get_user_by_id(1)
has_permission = await has_user_perm(user, 'edit', article)

if has_permission:
    print("User has permission to edit the article.")
else:
    print("User does not have permission to edit the article.")
```

### Example 4: Assigning Group Permissions

To assign the 'view' permission to a group for a specific object, you can use the following code:

```python
group = get_group_by_name('Viewers')
article = get_article_by_id(1)

await assign_group_perm('view', group, obj=article)
```

### Example 5: Revoking Group Permissions from Users

If you want to revoke the 'edit' permission from a group and also from the users within that group, you can do so as follows:

```python
group = get_group_by_name('Editors')

await assign_group_perm('edit', group, revoke=True, revoke_users_permissions=True)
```

## Conclusion

Managing user permissions is essential for maintaining security and proper access control in your application. The provided functions and methods allow you to assign, revoke, and check permissions for users and groups effectively. By following the examples and guidelines in this documentation, you can implement robust permission management in your application.
