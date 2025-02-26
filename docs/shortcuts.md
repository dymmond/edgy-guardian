# Shortcuts

## Introduction

In modern applications, managing user permissions is crucial for ensuring security and proper access control. This documentation provides a comprehensive guide on how to use the provided code to manage user permissions, groups, and content types effectively.

### What is a Permission?

A permission is a rule that defines what actions a user or group of users can perform on a specific object or resource within an application. Permissions are typically represented as strings, such as 'view', 'edit', or 'delete'.

### What is a Group?

A group is a collection of users that share common permissions. By assigning permissions to a group, you can manage access control for multiple users simultaneously. This simplifies the process of granting and revoking permissions.

### What is a Content Type?

A content type represents the type of object or resource for which permissions are being managed. For example, in a content management system, content types might include articles, images, and videos. Managing permissions at the content type level allows for fine-grained access control.

## Functions

### `has_user_perm`

#### Description

Checks if a user has a specific permission for a given object.

#### Signature

```python
async def has_user_perm(user: type[edgy.Model], perm: str, obj: Any) -> bool:
```

#### Parameters

- `user` (type[edgy.Model]): The user for whom the permission check is being performed.
- `perm` (str): The permission string to check (e.g., 'view', 'edit').
- `obj` (Any): The object for which the permission is being checked.

#### Returns

- `bool`: True if the user has the specified permission for the object, False otherwise.

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

#### Signature

```python
async def has_group_permission(user: type[edgy.Model], perm: str, obj: Any) -> bool:
```

#### Parameters

- `user` (type[edgy.Model]): The user for whom the permission check is being performed.
- `perm` (str): The permission string to check (e.g., 'view', 'edit').
- `obj` (Any): The object for which the permission is being checked.

#### Returns

- `bool`: True if the user has the specified permission for the object, False otherwise.

#### Example

```python
has_permission = await has_group_permission(user, 'edit', some_object)

if has_permission:
    print("User has permission to edit the object.")
else:
    print("User does not have permission to edit the object.")
```

### `assign_group_perm`

#### Description

Assigns or revokes a permission to/from a group, optionally for specific users and/or an object.

#### Signature

```python
async def assign_group_perm(
    perm: type[edgy.Model] | str,
    group: type[edgy.Model] | str,
    users: type[edgy.Model] | None = None,
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> None:
```

#### Parameters

- `perm` (str): The permission to assign or revoke. This should be a string representing the permission codename.
- `group` (type[edgy.Model]): The group to which the permission will be assigned or from which it will be revoked.
- `users` (type[edgy.Model] | None, optional): The users within the group for whom the permission will be assigned or revoked. Defaults to None.
- `obj` (Any | None, optional): The object for which the permission is assigned or revoked. Defaults to None.
- `revoke` (bool, optional): If set to True, the permission will be revoked from the group. Defaults to False.
- `revoke_users_permissions` (bool, optional): If set to True, the permission will also be revoked from the users within the group. Defaults to False.

#### Returns

- `None`

#### Example

```python
await assign_group_perm('edit', group, users=[user1, user2], obj=some_object)
await assign_group_perm('view', group, revoke=True)
await assign_group_perm('delete', group, revoke=True, revoke_users_permissions=True)
```

### `assign_perm`

#### Description

Assigns or revokes a permission for a user or group on a specific object.

#### Signature

```python
async def assign_perm(perm: str, users: Any, obj: Any | None = None, revoke: bool = False) -> None:
```

#### Parameters

- `perm` (str): The permission to assign or revoke. This should be a string representing the permission name.
- `users` (Any): The user or group to assign or revoke the permission for. This can be an instance of a User or Group model.
- `obj` (Any, optional): The object to assign or revoke the permission for. This can be any object for which permissions are managed. Defaults to None, meaning the permission is assigned or revoked globally.
- `revoke` (bool, optional): If True, the permission will be revoked instead of assigned. Defaults to False.

#### Returns

- `None`

#### Example

```python
# Assign the 'edit' permission to a user for a specific object
await assign_perm('edit', user_instance, obj=some_object)

# Revoke the 'delete' permission from a group globally
await assign_perm('delete', group_instance, revoke=True)
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
