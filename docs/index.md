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

Edgy Guardian brings the concept of `ContentType`, `Group` and `Permission` into any application
using Edgy.

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

## Introduction

### **ContentType**

The `ContentType` model represents all the models in an application, allowing permissions to be assigned dynamically to specific models. It is primarily used in conjunction with Edgy Guardian's permissions system to define access controls at a model level. Each `ContentType` entry corresponds to a model in a specific application, storing metadata such as the app label and model name. This enables generic relationships, making it possible to manage permissions and interactions with different models in a flexible way.  

### **Group**

A `Group` is a way to collectively manage permissions for multiple users. Instead of assigning individual permissions to each user, groups allow permissions to be granted in bulk, making access control easier to maintain. Users can be added to one or more groups, inheriting the permissions associated with them. This is particularly useful in large systems where different roles (e.g., "Editors", "Moderators", "Admins") require specific sets of permissions.  

### **Permission**

The `Permission` model defines specific actions that a user or group can perform on a given model. Each permission is linked to a `ContentType`, indicating which model it applies to, and has a unique `codename` (such as `add_user`, `change_post`, or `delete_comment`). Permissions can be assigned directly to users or through groups, providing granular control over what actions are allowed within an application. This system helps enforce security and role-based access management.

## How to use it

Edgy Guardian introduces the concept of `apps`. If you are familiar with Django, there is always a
`apps.py` file generated on each installed apps.

Edgy Guardian **introduces** the same concept and **it is mandatory to declared them** or it won't
be possible to leverage the library.

Edgy Guardian **requires** the following:

* [Apps](#the-apps) - Where we declare an existance of an app in the system. Each app contains models.
* [ContentType](#contenttype-model) - The ContentType model, this is crucial for Edgy Guardian to operate.
* [Permission model](#permissions-model) - The permissons model where the magic will happen.
* [Groups model](#groups-model) - This **is not mandatory** but if used, it will **be required some steps**.
* [User model](#user-model) - The application user model using the library.
* [EdgyGuardian config](#edgyguardian-config) - The **essential configuration** for Edgy Guardian to operate.
* [handle_content_types](#handle_content_types) - The essential function to manage the content types automatically.

### The apps

Imagine the following structure as example of the `apps.py` being applied in your project using Edgy.

```markdown
.
└── guardian
    ├── apps
    │   ├── accounts
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── contenttypes
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── __init__.py
    │   ├── items
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── permissions
    │   │   ├── apps.py
    │   │   ├── __init__.py
    │   │   └── models.py
    │   └── products
    │       ├── apps.py
    │       ├── __init__.py
    │       └── models.py
    ├── __init__.py
    └── main.py
```

This structure assumes a clean separation of what is what but **you are free** to do it on your own.

Each `apps.py` contains some basic information that is used by [EdgyGuardian](#edgyguardian-config).

The `apps.py` **must** implement the `AppConfig` from Edgy Guardian.

**Example**

Using the `contenttypes` as example.

```python
from edgy_guardian.apps import AppConfig


class ContentTypesConfig(AppConfig):
    name: str = "contenttypes"
    verbose_name: str = "Content Types"
```

As you can see, you need to implement the `AppConfig` from:

```python
from edgy_guardian.apps import AppConfig
```

Then the `name` and `verbose_name` are **mandatory fields**. The `name` its what it will be used
to populate the `app_name` in the `ContentType` table in the database once the migrations happen.

!!! Warning
    Every `apps.py` must **only exist** in the modules that contain Edgy models.

### ContentType Model

Edgy Guardian operates in a simple but powerful way and it provides out of the box `ContentType`s
model that you **only need to inherit the `BaseContentType`** for the migrations to be applied.

```python
import edgy

from edgy_guardian.content_types.models import BaseContentType

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)

class ContentType(BaseContentType):
    class Meta:
        registry = settings.registry

```

This example its how you use it but the **registry** should be **your shared registry** across the codebase.

### Permissions Model

The `Permission` model is where all the magic happens, its the most powerful object/model that you will
be using with Edgy Guardian.

The `Permission` must be **also inherited** from the `BasePermission`, you can name it whatever you
want to name but **you must inherit from `BasePermission`**.

Now **there is also an additional field you must add**.

For the `Permission` model to work, you **must** add the `users` attribute into your `Permission`
model and **must** be of type `edgy.ManyToManyField`.

Why do you need to do this?

Well, first, permissions are associated to a `User` model. That user model can be **any model** of your
own application, it is not linked to any `users` of Edgy Guardian and this brings the flexibility
of coupling the Edgy Guardian `BasePermission` with **any Edgy model** that represents a user in 
any application.

Extra steps? Yes, but flexibility comes with some extras but its worth in the end.

```python
import edgy

from edgy_guardian.permissions.models import BasePermission

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)


class Permission(BasePermission):
    users: list[edgy.Model] = edgy.ManyToManyField(  # type: ignore
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="permissions"
    )

    class Meta:
        registry = registry
```

So, to be clear, you **must inherit from `BasePermission`** and **add a `users`** pointing to your
application `User` model.

### Groups Model

Now, what is this? Well, as the [definition of Group](#group) defines, the groups allow `in bulk` permission
assignment instead of individual permissions.

The `Group` model **it is not mandatory** but if you want to use the functionalities that come with it,
then you also **must inherit from the `BaseGroup`** model provided by Edgy Guardian and add not one
but two **extra attributes**.

In the same way the `users` was added into `Permission`, the same must be done for `Group` with the
addition of **also adding** the `permissions` attribute.

The `permissions` attribute **must** be of type `edgy.ManyToManyField` in the same way the `users` must also be.

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
        "Permission",
        through_tablename=edgy.NEW_M2M_NAMING,
        related_name="groups",
    )

    class Meta:
        registry = settings.registry
```

Again, like for [Permission](#permission), this must be done because of flexibility and you might
call the `Permission` model, something else, as long as in the `Group` the attribute is still
called `permissions` and the field is a `edgy.ManyToManyField` pointing to your permissions model.

### User Model

This is your application user model It does not matter how you have it and what do you have it.

The [EdgyGuardian Config](#edgyguardian-config) will take care of the rest.

**Example**

```python
from datetime import datetime
from typing import Any

import edgy

database = edgy.Database("sqlite:///db.sqlite")
registry = edgy.Registry(database=database)


class User(edgy.Model):
    """
    Base model used for a custom user of any application.
    """

    first_name: str = edgy.CharField(max_length=150)
    last_name: str = edgy.CharField(max_length=150)
    username: str = edgy.CharField(max_length=150, unique=True)
    email: str = edgy.EmailField(max_length=120, unique=True)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)  # type: ignore
    is_staff: bool = edgy.BooleanField(default=False)  # type: ignore
    is_superuser: bool = edgy.BooleanField(default=False)  # type: ignore

    class Meta:
        registry = registry
```

### EdgyGuardian Config

This is **the most import object** that tights everything together. For your application to work
properly, you **must declare** the `edgy_guardian` configuration inside your
[EdgySettings](https://edgy.tarsild.io/settings/) and load it via `EDGY_SETTINGS_MODULE` as explained
in the [official documentation](https://edgy.tarsild.io/settings/)

Remember all of those models declared previously? Also remember the [apps](#the-apps) structure?

Let us now tight everything together in the Edgy Guardian Config.

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

Now, what is this? Well, [Edgy](https://edgy.dymmond.com) has the normal `preloads` that is used
to generate the migrations for you application and the `edgy_guardian` is what this library needs
to operate.

* **models** - A dictionary containing a `name` (usually the name of the app) and the `location`
of where the models are. Egy Guardian does not use the `preloads` as separation.
* **apps** - A list containing the location where the `apps.py` files are in each app.
* **content_type_model** - A string with the name given to the `ContentType` model.
* **user_model** - The name of the `User` model of the application.
* **permission_model** - The name of the `Permission` model declared. **Its the one you define**.
* **group_model** - The name given to the `Group` model. **Its the one you define**

This will be used in the [initialise application](#initialise-your-application) where it will make sense
why this needs to happen.

There is an additional step to be made but that is from the application initialiser itself.

### handle_content_types

This is **crucial** to tight the system all together. This is the function that `on_startup` will
create the `content types` **automatically** for you as well as remove those that no longer exist.

E.g.: Migrations that remove models.

How to import it?

```python
from edgy_guardian.loader import handle_content_types
```

### Initialise Your Application

This is where we start an application using **Edgy** and **Edgy Guardian** and where all comes together.

The same author of Edgy its also the same of [Esmerald](https://esmerald.dev) so for this example
we will be using it but **feel free to use any other framework**.

```python
#!/usr/bin/env python
"""
Generated by 'esmerald createproject' using Esmerald 3.6.7.
"""

import os
import sys

from esmerald import Esmerald

from edgy_guardian.loader import handle_content_types


def build_path():
    """
    Builds the path of the project and project root.
    """
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        sys.path.append(os.path.join(SITE_ROOT, "apps"))


def get_application():
    """
    This is optional. The function is only used for organisation purposes.
    """
    build_path()
    from edgy import Instance, monkay
    from edgy.conf import settings as edgy_settings
    from esmerald.conf import settings

    # Initialise the registry and pass it to `edgy_guardian`.
    edgy_settings.edgy_guardian.register(settings.registry)

    # ensure the settings are loaded
    monkay.evaluate_settings(
        ignore_preload_import_errors=False,
        onetime=False,
    )

    app = Esmerald(
        on_startup=[
            settings.registry.__aenter__,
            handle_content_types,
        ],
        on_shutdown=[settings.registry.__aexit__],
    )
    monkay.set_instance(Instance(registry=app.settings.registry, app=app))
    return app


app = get_application()
```

As you can see, we apply the Edgy normal configurations for migrations and we pass the global
application registry into `edgy_guardian.register(registry)`.

This last step its what activates **everything** in Edgy Guardian and now you are ready to start
using it.

## Next Steps

Learn how to use the system by [using the shortcuts](./shortcuts.md).
