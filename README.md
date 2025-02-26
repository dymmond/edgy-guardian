# Edgy Guardian

<p align="center">
  <a href="https://edgy.dymmond.com"><img src="https://res.cloudinary.com/tarsild/image/upload/v1690804138/packages/edgy/logo_wvmjxz.png" alt='Edgy'></a>
</p>

<p align="center">
    <em>🔥 Per object permissions for Edgy 🔥</em>
</p>

---

**Documentation**: [https://edgy-guardian.dymmond.com](https://edgy-guardian.dymmond.com) 📚

**Source Code**: [https://github.com/dymmond/edgy-guardian](https://github.com/dymmond/edgy-guardian)

---

Edgy Guardian is an object-level permissions library for the **Edgy** framework, inspired by Django Guardian. It extends Edgy's built-in permission system by allowing fine-grained, per-object access control, making it ideal for applications that require more precise authorization mechanisms.

## Motivation

While Edgy provides a robust permission system, it operates mainly at the model level. However, many real-world applications require per-object permissions—for example:

- A document management system where users should only access specific documents they own.
- A multi-tenant application where different users or groups have different levels of access to individual objects.
- A social media platform where posts, comments, and messages have custom visibility settings.

Edgy Guardian fills this gap by introducing a flexible and efficient object-level permission system, inspired by the battle-tested Django Guardian.

### Edgy Permissions

Edgy also brings [native permissions](https://edgy.tarsild.io/permissions/intro/) and it can be used
out of the box as well. The way it is done is slighly different from Edgy Guardian and aims something
slighly different.

!!! Warning
    For now, Edgy Guardian only operates with normal primary keys (pk, id) and not with complex primary
    keys offered by Edgy. 

    The reason for this is to make sure 99% of the use cases are covered but this does not mean it
    won't be supported in the future.

## Requirements

To use Edgy Guardian, ensure your environment meets the following requirements:

- **Python 3.10+** (Edgy Guardian leverages modern Python features that require version 3.10 or higher)
- **Edgy framework** (Ensure you have Edgy installed and configured in your project)

## Installation

To install Edgy Guardian, simply use pip:

```sh
pip install edgy-guardian
```

## Usage

### Assigning Object-Level Permissions

Once installed, you can assign object-level permissions using the provided API. Example:

```python
from edgy_guardian.shortcuts import assign_perm
from myapp.models import Project

project = Project.objects.get(id=1)
user = User.objects.get(username="john_doe")
assign_perm("view_project", user, project)
```

### Checking Object-Level Permissions

You can check if a user has permission for a specific object:

```python
from edgy_guardian.shortcuts import has_perm

if has_perm(user, "view_project", project):
    print("User can view this project!")
```

### Removing Permissions

To revoke an object-level permission:

```python
from edgy_guardian.shortcuts import remove_perm

remove_perm("view_project", user, project)
```

## Features

- **Granular object-level permissions** for better access control.
- **Easy API** for assigning, checking, and removing permissions.
- **Seamless integration** with Edgy's existing authentication and authorization system.
- **Support for both user and group permissions**, allowing flexible access control mechanisms.


## License

Edgy Guardian is released under the BSD-3 Clause License.

## Acknowledgments

This project is heavily inspired by **Django Guardian**, adapting its concepts to the **Edgy** framework.

