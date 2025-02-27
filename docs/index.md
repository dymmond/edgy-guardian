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

Edgy Guardian is a library that adds object-level permissions to the **Edgy** framework, inspired by Django Guardian. It enhances Edgy's permission system by allowing fine-grained, per-object access control, making it perfect for applications needing precise authorization.

## Why Use Edgy Guardian?

Edgy's built-in permission system works at the model level, but many applications need per-object permissions. For example:

- Document management systems where users access only their documents.
- Multi-tenant applications with different access levels for different users or groups.
- Social media platforms with custom visibility settings for posts, comments, and messages.

Edgy Guardian addresses this need by introducing a flexible and efficient object-level permission system.

The following steps explains how to quickly setup Edgy Guardian and it must be followed properly.

This documentation also provides explanations how to use Edgy Guardian features effectively.

## Key Concepts

### Edgy Permissions

Edgy provides [native permissions](https://edgy.tarsild.io/permissions/intro/) that work out of the box. Edgy Guardian offers a different approach for more specific use cases.

!!! Warning
    Currently, Edgy Guardian only supports normal primary keys (pk, id), not complex primary keys. This covers most use cases, but future support is planned.

## Requirements

To use Edgy Guardian, ensure your environment meets these requirements:

- **Python 3.10+** (Edgy Guardian uses modern Python features)
- **Edgy framework** (Ensure Edgy is installed and configured in your project)

## Installation

Install Edgy Guardian using pip:

```sh
pip install edgy-guardian
```

## Introduction

### **ContentType**

The `ContentType` model represents all models in an application, allowing dynamic assignment of permissions to specific models. It stores metadata like app label and model name, enabling flexible management of permissions and interactions with different models.

### **Group**

A `Group` allows collective management of permissions for multiple users. Instead of assigning permissions individually, groups enable bulk permission assignments, simplifying access control. Users inherit permissions from the groups they belong to, useful for roles like "Editors", "Moderators", and "Admins".

### **Permission**

The `Permission` model defines specific actions users or groups can perform on a model. Each permission is linked to a `ContentType` and has a unique `codename` (e.g., `add_user`, `change_post`). Permissions can be assigned directly to users or through groups, providing granular control over actions within an application.

## How to Use Edgy Guardian

Edgy Guardian introduces the concept of `apps`. Each installed app must declare an `apps.py` file, similar to Django.

### The Apps

Here's an example structure for `apps.py` in your project:

```markdown
.
└── guardian
    ├── apps
    │   ├── accounts
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── contenttypes
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── __init__.py
    │   ├── items
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── permissions
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   └── products
    │       ├── apps.py
    │       ├── __init__.py
    │       └── models.py
    ├── __init__.py
    └── main.py
```

Each `apps.py` must implement the `AppConfig` from Edgy Guardian.

**Example**

Using `contenttypes` as an example:

```python
from edgy_guardian.apps import AppConfig

class ContentTypesConfig(AppConfig):
    name: str = "contenttypes"
    verbose_name: str = "Content Types"
```

### ContentType Model

Edgy Guardian provides out-of-the-box `ContentType` models. Inherit from `BaseContentType` for migrations:

```python
import edgy
from edgy_guardian.content_types.models import BaseContentType

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)

class ContentType(BaseContentType):
    class Meta:
        registry = settings.registry
```

### Permissions Model

The `Permission` model is powerful and must inherit from `BasePermission`. Add a `users` attribute of type `edgy.ManyToManyField`:

```python
import edgy
from edgy_guardian.permissions.models import BasePermission

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)

class Permission(BasePermission):
    users: list[edgy.Model] = edgy.ManyToManyField(
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="permissions"
    )

    class Meta:
        registry = registry
```

### Groups Model

The `Group` model is optional but useful for bulk permission assignments. Inherit from `BaseGroup` and add `users` and `permissions` attributes:

```python
import edgy
from edgy_guardian.permissions.models import BaseGroup

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)

class Group(BaseGroup):
    users: list[edgy.Model] = edgy.ManyToManyField(
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="groups"
    )
    permissions: list[Permission] = edgy.ManyToManyField(
        "Permission", through_tablename=edgy.NEW_M2M_NAMING, related_name="groups"
    )

    class Meta:
        registry = settings.registry
```

### User Model

Your application user model can be any model. Here's an example:

```python
from datetime import datetime
import edgy

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)

class User(edgy.Model):
    first_name: str = edgy.CharField(max_length=150)
    last_name: str = edgy.CharField(max_length=150)
    username: str = edgy.CharField(max_length=150, unique=True)
    email: str = edgy.EmailField(max_length=120, unique=True)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)
    is_staff: bool = edgy.BooleanField(default=False)
    is_superuser: bool = edgy.BooleanField(default=False)

    class Meta:
        registry = registry
```

### EdgyGuardian Config

This configuration ties everything together. Declare the `edgy_guardian` configuration inside your `EdgySettings`:

```python
from edgy import EdgySettings as BaseSettings
from edgy_guardian.configs import EdgyGuardianConfig

class EdgyAppSettings(BaseSettings):
    preloads: list[str] = [
        "accounts.models",
        "permissions.models",
        "contenttypes.models",
        "products.models",
        "items.models",
    ]
    edgy_guardian: EdgyGuardianConfig = EdgyGuardianConfig(
        models={
            "accounts": "accounts.models",
            "contenttypes": "contenttypes.models",
            "permissions": "permissions.models",
            "products": "products.models",
            "items": "items.models",
        },
        apps=[
            "accounts.apps.AccountsConfig",
            "permissions.apps.PermissionsConfig",
            "contenttypes.apps.ContentTypesConfig",
            "products.apps.ProductsConfig",
            "items.apps.ItemsConfig",
        ],
        content_type_model="ContentType",
        user_model="User",
        permission_model="Permission",
        group_model="Group",
    )
```

### handle_content_types

This function automatically manages content types on startup:

```python
from edgy_guardian.loader import handle_content_types
```

### Initialize Your Application

Here's how to start an application using Edgy and Edgy Guardian:

```python
#!/usr/bin/env python
import os
import sys
from esmerald import Esmerald
from edgy_guardian.loader import handle_content_types

def build_path():
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        sys.path.append(os.path.join(SITE_ROOT, "apps"))

def get_application():
    build_path()
    from edgy import Instance, monkay
    from edgy.conf import settings as edgy_settings
    from esmerald.conf import settings

    edgy_settings.edgy_guardian.register(settings.registry)
    monkay.evaluate_settings(ignore_preload_import_errors=False, onetime=False)

    app = Esmerald(
        on_startup=[settings.registry.__aenter__, handle_content_types],
        on_shutdown=[settings.registry.__aexit__],
    )
    monkay.set_instance(Instance(registry=app.settings.registry, app=app))
    return app

app = get_application()
```

## Next Steps

Learn how to use the system by [using the shortcuts](./shortcuts.md).
