# Edgy Guardian: Simple how to

In this section we will be building a simple application using Edgy Guardian and for that we will
be using [Esmerald](https://esmerald.dev) as a framework since it uses it gives a lot of the
boilerplate we can use to speed up.

You are free to ignore the use of Esmerald if your preferred framework is something else, like
FastAPI, Starlette, Litestar, Sanic, Quartz...

The same principle is still applied.

For this simple tutorial we will be having in the end an application that contains Edgy Guardian
running.

## Notes

As mentioned, Esmerald will be used but you are free to use any other of your choice.

## The Application Structure

THe application in the end will have a similar structure to the following:

```markdown
.
└── guardian
    ├── __init__.py
    ├── apps
    │   ├── __init__.py
    │   ├── accounts
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   └── models.py
    │   ├── contenttypes
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   └── models.py
    │   ├── items
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   └── models.py
    │   ├── permissions
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   └── models.py
    │   └── products
    │       ├── __init__.py
    │       ├── apps.py
    │       └── models.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── edgy.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    └── main.py
```

### Create the application

You can start by installing [Esmerald](https://esmerald.dev) and [Edgy](https://edgy.dymmond.com).

```shell
pip install esmerald edgy
```

#### Create the application scaffold

You can manually create everything by youself but since we use Esmerald, let us take advantage of it
and use its directives to generate a ready to go project.

```shell
esmerald createproject guardian
```

This will generate all the files similar to the structure above. In fact, more files are generated
like a Taskfile, gitignore, README and so on but lets not focus on that.

#### Create the apps

Again, Esmerald provides a lot of directives and one of those is the concept of `apps` which its
very handy for Edgy Guardian, saves a lot of time.

Let us create the apps listed above, for this you will need to `cd` to the `guardian/apps` folder
and run:

```shell
esmerald createapp accounts
esmerald createapp contenttypes
esmerald createapp permissions
esmerald createapp items
esmerald createapp products
```

If you have a look at any of those apps, you will see that a lot of files are automatically generated
that are not listed in the folder structure above, like `v1` and `directives`, why? Because we don't need it
for this example, so either you remove, or you ignore them as we won't be developing any API in this example.

#### Create the `apps.py` file

Well, Esmerald is great but its not an oracle (not yet at least). As mentioned numerous times in this
documentation, Edgy Guardian introduces the concept of `apps.py` and therefore we **must** add it
into our `apps` conveniently generated for us by Esmerald.

So, lets do it.

On each `app` create an `apps.py`.

Now its time to add some information on it.

##### Accounts

```python
from edgy_guardian.apps import AppConfig


class AccountsConfig(AppConfig):
    name: str = "accounts"
    verbose_name: str = "Accounts"
```

##### Content Types

```python
from edgy_guardian.apps import AppConfig


class ContentTypesConfig(AppConfig):
    name: str = "contenttypes"
    verbose_name: str = "Content Types"
```

##### Permissions

```python
from edgy_guardian.apps import AppConfig


class PermissionsConfig(AppConfig):
    name: str = "permissions"
    verbose_name: str = "Permissions"
```

##### Items

```python
from edgy_guardian.apps import AppConfig


class ItemsConfig(AppConfig):
    name: str = "items"
    verbose_name: str = "Items"
```

##### Products

```python
from edgy_guardian.apps import AppConfig


class ProductsConfig(AppConfig):
    name: str = "products"
    verbose_name: str = "Products"
```

#### Create the models

Now this is where we create the models to be used by our application and where we start linking
everything.

We won't be talking about the hows and the whys as the documentation mentioned this as well.

Now, before doing this bit, **let us assume** that thw `configs/settings.py` contains a `cached_property`
called `registry` (Edgy setup) and that registry will be used across all of the models.

The registry its what makes everything work in Edgy.

##### Accounts

```python
from datetime import datetime
from typing import Any

import edgy
from esmerald.conf import settings

from edgy_guardian.mixins import UserMixin


class User(edgy.Model, UserMixin):
    """
    Base model used for a custom user of any application.
    """

    first_name: str = edgy.CharField(max_length=150)
    last_name: str = edgy.CharField(max_length=150)
    username: str = edgy.CharField(max_length=150, unique=True)
    email: str = edgy.EmailField(max_length=120, unique=True)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)  
    is_staff: bool = edgy.BooleanField(default=False)  
    is_superuser: bool = edgy.BooleanField(default=False)  

    class Meta:
        registry = settings.registry
```

##### Content Types

```python
from esmerald.conf import settings

from edgy_guardian.content_types.models import BaseContentType


class ContentType(BaseContentType):
    class Meta:
        registry = settings.registry
```

Remember that we **must** inherit from the `BaseContentType`.

##### Permissions

```python
import edgy
from esmerald.conf import settings

from edgy_guardian.permissions.models import BaseGroup, BasePermission


class Group(BaseGroup):
    users: list[edgy.Model] = edgy.ManyToManyField(
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="groups"
    )
    permissions: list[BasePermission] = edgy.ManyToManyField(  
        "Permission",
        through_tablename=edgy.NEW_M2M_NAMING,
        related_name="groups",
    )

    class Meta:
        registry = settings.registry


class Permission(BasePermission):
    users: list[edgy.Model] = edgy.ManyToManyField(
        "User", through_tablename=edgy.NEW_M2M_NAMING, related_name="permissions"
    )

    class Meta:
        registry = settings.registry
```

Remember that we **must inherit** from `BasePermission` and add a **mandatory** `users` field as
`edgy.ManyToManyField` and if we also use `Group` then the `BaseGroup` **must be inherited** and
`users` and `permissions` are **mantatory fields** to be added.

##### Items

```python
import edgy
from esmerald.conf import settings


class Item(edgy.Model):
    name: str = edgy.CharField(max_length=255)
    description: str = edgy.TextField()

    class Meta:
        registry = settings.registry
```

##### Products

```python
import edgy
from esmerald.conf import settings


class Product(edgy.Model):
    name: str = edgy.CharField(max_length=255)
    description: str = edgy.TextField()

    class Meta:
        registry = settings.registry
```

#### Create an `edgy.py`

Now its time to create the `edgy.py` (or whatever you want to call) inside the `guardian/configs/`.

Those will be the new settings that Edgy will look at when looking for the `EDGY_SETTINGS_MODULE`.

Let us populate with the information required for the Edgy Guardian and Edgy to operate, for this
we will be importing the `EdgyGuardianConfig` from `edgy_guardian.configs`.

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

#### Create the `main.py` (or app.py) file

Here its where we tie everything together in one Esmerald instance.

We will be using the **mandatory `handle_content_types`** function to make sure we will be able to
use the Edgy Guardian and generate the Content Types automatically.

```python
import os
import sys
from contextlib import asynccontextmanager

from esmerald import Esmerald, settings

from edgy_guardian.loader import handle_content_types


@asynccontextmanager
async def lifespan(app: Esmerald):
    async with settings.registry:
        await handle_content_types()
        yield


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
        lifespan=lifespan,
    )
    monkay.set_instance(Instance(registry=app.settings.registry, app=app))
    return app


app = get_application()
```

Let's break down the provided code step by step:

##### Imports

```python
import os
import sys
from contextlib import asynccontextmanager

from esmerald import Esmerald, settings

from edgy_guardian.loader import handle_content_types
```

- **os** and **sys**: These modules provide functions to interact with the operating system and manipulate the Python runtime environment.
- **asynccontextmanager**: This decorator from `contextlib` is used to define asynchronous context managers.
- **Esmerald** and **settings**: These are imported from the `esmerald` framework, which is similar to Starlette or FastAPI.
- **handle_content_types**: This function is imported from `edgy_guardian.loader` and is used to manage content types within the application.

##### Lifespan Context Manager

```python
@asynccontextmanager
async def lifespan(app: Esmerald):
    async with settings.registry:
        await handle_content_types()
        yield
```

- **@asynccontextmanager**: This decorator is used to create an asynchronous context manager.
- **lifespan**: This function defines the lifespan of the application. It ensures that certain tasks are performed during the application's startup and shutdown phases.
- **async with settings.registry**: This line ensures that the application's settings registry is properly managed during the lifespan.
- **await handle_content_types()**: This line calls the `handle_content_types` function to manage the content types before yielding control back to the application.
- **yield**: This allows the application to run while the context manager is active.

##### Build Path Function

```python
def build_path():
    """
    Builds the path of the project and project root.
    """
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        sys.path.append(os.path.join(SITE_ROOT, "apps"))
```

- **build_path**: This function sets up the project's root path and ensures that it is included in the Python path (`sys.path`).
- **SITE_ROOT**: This variable stores the absolute path of the directory containing the current script.
- **sys.path.append**: These lines add the project root and the "apps" directory to the Python path, allowing the application to import modules from these directories.

##### Get Application Function

```python
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
        lifespan=lifespan,
    )
    monkay.set_instance(Instance(registry=app.settings.registry, app=app))
    return app
```

- **get_application**: This function sets up and returns the Esmerald application instance.
- **build_path()**: Calls the `build_path` function to set up the project paths.
- **from edgy import Instance, monkay**: Imports `Instance` and `monkay` from the `edgy` module.
- **from edgy.conf import settings as edgy_settings**: Imports settings from `edgy.conf` and aliases it as `edgy_settings`.
- **from esmerald.conf import settings**: Imports settings from `esmerald.conf`.
- **edgy_settings.edgy_guardian.register(settings.registry)**: Registers the settings registry with `edgy_guardian`.
- **monkay.evaluate_settings**: Ensures that the settings are loaded and evaluated.
- **app = Esmerald(lifespan=lifespan)**: Creates an instance of the Esmerald application, passing the `lifespan` context manager.
- **monkay.set_instance(Instance(registry=app.settings.registry, app=app))**: Sets the application instance with the registry and the application itself.
- **return app**: Returns the configured Esmerald application instance.

##### Application Instance

##### Summary

- **Imports**: The code imports necessary modules and functions.
- **Lifespan Context Manager**: Manages the application's lifespan, ensuring content types are handled.
- **Build Path**: Sets up the project paths.
- **Get Application**: Configures and returns the Esmerald application instance.

#### Start the application

Now this its where we start the application but first we need to generate some `migrations` to make
sure we have the database operational.

To make our lives easier, lets export some environment varibles required by Edgy to make sure we
can run everything smoothly.

```shell
export ESMERALD_SETTINGS_MODULE=guardian.configs.settings.AppSettings
export EDGY_SETTINGS_MODULE=guardian.configs.edgy.EdgyAppSettings

# A connection string to your local database
export EDGY_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/guardian
```

For this in the root of your project, run:

```shell
edgy init
```

This will create the `migrations` folder used by Edgy. Then we can generate the migration files.

```shell
edgy makemigrations
```

Now we can run the migrations:

```shell
edgy migrate
```

With all of this steps done properly, that can also be checked in the [official documentation of Edgy](https://edgy.dymmond.com/migrations/migrations), we
can move forward to the application start.

Since we already exported our environment variables to make it easier for us, we can simply start the application.

* **ESMERALD_SETTINGS_MODULE** - Where Esmerald should look for settings.
* **EDGY_SETTINGS_MODULE** - The new `edgy.py` previously created.
* **EDGY_DATABASE_URL** - The database URL used by Edgy and migrations.

```shell
uvicorn guardian.main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

##### Access the database

If everything went smoothly (or some minor changes happened because you did in a different way), you
should now have all the tables migrated and if you **query** the `contenttypes` table you should
also have records already populated.

**You are now ready to use Edgy Guardian**.

Have a look at the [shortcuts](./shortcuts.md) and [mixins](./mixins.md) and see how can you take
advantage of those and leverage the permissions.
