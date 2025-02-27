# `UserMixin` Class

## Overview

The `UserMixin` class is a mixin designed to add permission methods to a User model. This mixin provides methods for assigning, revoking, and checking permissions for a user or a user's group. It leverages asynchronous methods to interact with the permissions model.

## UserMixin Class

```python
class UserMixin: ...
```

This is how you can import the `UserMixin`.

```python
from edgy_guardian.mixins import UserMixin
```

**Example**

```python
import edgy

from edgy_guardian.mixins import UserMixin


class User(edgy.Model, UserMixin): ...
```

From here on, every `user` object will have automatically access to the available functions of the
`UserMixin`.

### Explanation

- The `UserMixin` class is defined as a mixin to extend the User model with permission-related methods.

#### Methods

##### has_perm

```python
async def has_perm(self, perm: str, obj: Any) -> bool:
```

###### Explanation

- **Purpose**: Checks if the user has a specific permission on a given object.
- **Arguments**:
  - **`perm`**: The permission to check.
  - **`obj`**: The object to check the permission on.

##### assign_perm

```python
async def assign_perm(
    self, perm: str | type[edgy.Model], obj: Any | None = None, revoke: bool = False
) -> Any:
```

###### Explanation

- **Purpose**: Assigns or revokes a specific permission for the user.
- **Arguments**:
  - **`perm`**: The permission to assign or revoke.
  - **`obj`**: The object to assign or revoke the permission for. Defaults to `None`.
  - **`revoke`**: If `True`, the permission will be revoked; if `False`, the permission will be assigned. Defaults to `False`.

##### assign_group_perm

```python
async def assign_group_perm(
    self,
    perm: str | type[edgy.Model],
    group: Any | type[edgy.Model],
    obj: Any | None = None,
    revoke: bool = False,
    revoke_users_permissions: bool = False,
) -> None:
```

###### Explanation

- **Purpose**: Assigns or revokes a specific permission for the user's group.
- **Arguments**:
  - **`perm`**: The permission to assign or revoke.
  - **`group`**: The group to assign or revoke the permission for.
  - **`obj`**: The object to assign or revoke the permission for. Defaults to `None`.
  - **`revoke`**: If `True`, the permission will be revoked; if `False`, the permission will be assigned. Defaults to `False`.
  - **`revoke_users_permissions`**: If `True`, the permission will also be revoked from the user. Defaults to `False`.

##### has_group_permission

```python
async def has_group_permission(self, perm: str | type[edgy.Model], obj: Any) -> bool:
```

###### Explanation

- **Purpose**: Checks if the user's group has a specific permission on a given object.
- **Arguments**:
  - **`perm`**: The permission to check.
  - **`obj`**: The object to check the permission on.

##### remove_perm

```python
async def remove_perm(self, perm: str | type[edgy.Model], obj: Any | None = None) -> None:
```

###### Explanation

- **Purpose**: Removes a specific permission from the user.
- **Arguments**:
  - **`perm`**: The permission to remove.
  - **`obj`**: The object to remove the permission from. Defaults to `None`.

Got it! Let's add the `remove_group_perm` method to the Markdown documentation:

##### remove_group_perm

```python
async def remove_group_perm(
    self,
    perm: str | type[edgy.Model],
    group: str | type[edgy.Model],
    obj: Any | None = None,
    revoke_users_permissions: bool = False,
) -> None:
```

###### Explanation

- **Purpose**: Removes a specific permission from the user's group.
- **Arguments**:
  - **`perm`**: The permission to remove.
  - **`group`**: The group to remove the permission from.
  - **`obj`**: The object to remove the permission from. Defaults to `None`.
  - **`revoke_users_permissions`**: If `True`, the permission will also be revoked from the user. Defaults to `False`.
```
