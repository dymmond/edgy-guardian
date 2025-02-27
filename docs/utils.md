# Utilities

Edgy Guardian has a set of utilities that can and a few **must** be used to make sure its running
in the right way.

To make sure you always have the [ContentType](./index.md#contenttype) up to date, there is a
mandatory function that **must always** be executed, the `handle_content_types`.

## handle_content_types

Sure, here's a more detailed explanation of the `handle_content_types` function:

```python
async def handle_content_types() -> None:
```

This is how you import it:

```python
from edgy_guardian.loader import handle_content_types
```

#### Purpose

The `handle_content_types` function is designed to manage the content types within your application. Content types are a way to keep track of the different models (data structures) that your application uses. This function ensures that all models registered with the application have corresponding content types in the database.

#### Functionality

1. **Initialization**:
    - The function is asynchronous (`async`), meaning it can perform non-blocking operations, which is useful for I/O-bound tasks like database queries.
    - It should be run before any other operations that involve content types or permissions to ensure that the content types are correctly set up.

2. **Fetching Existing Content Types**:
    - The function retrieves all existing content types from the database.
    - If the content types app/model is not installed, it raises a `GuardianImproperlyConfigured` exception.

3. **Identifying Deleted Apps**:
    - It checks the existing content types against the current models registered in the application.
    - If a content type corresponds to a model that is no longer registered, it marks this content type for deletion.

4. **Identifying New Apps**:
    - It identifies new models that need content types created.
    - It ensures that these new models are added to the content types table.

5. **Deleting Old Content Types**:
    - It deletes content types for models that are no longer registered with the application.

6. **Creating New Content Types**:
    - It creates content types for new models that have been registered with the application.

7. **Logging**:
    - The function logs the successful management of content types, which is useful for monitoring and debugging.

#### Usage

- **Lifespan Event**: The function is ideally run during the application's lifespan events, such as `on_startup` or `on_shutdown`. This ensures that the content types are managed at the appropriate time in the application's lifecycle.
- **ASGI Integration**: Similar to Esmerald, Starlette, FastAPI... Those also supports lifespan events. You can integrate this function into any  `on_startup` event to ensure it runs when the application starts.

### Example Integration with Esmerald

```python
from esmerald import Esmerald


async def startup_event():
    await handle_content_types()

async def shutdown_event(): ...


app = Esmerald(
    on_startup=[startup_event],
    on_shutdown=[shutdown_event]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Or even using the `lifespan`.


```python
from contextlib import asynccontextmanager
from esmerald import Esmerald

from edgy_guardian.loader import handle_content_types


@asynccontextmanager
async def lifespan(app: Esmerald):
    await handle_content_types()
    yield


app = Esmerald(
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```


In this example:

- The `handle_content_types` function is called during the `startup` event of the Esmerald application.
- This ensures that the content types are managed before any other operations that depend on them.

## Apps

Sure, here's a detailed explanation of the provided code:

### Overview

This code defines a configuration system for managing applications and their models within a larger application framework. It includes two main classes: `AppConfig` and `Apps`.

You can import it via:

```python
from edgy_guardian.apps import get_apps
```

#### AppConfig Class

```python
class AppConfig(BaseModel): ...
```
- **AppConfig**: This class inherits from `BaseModel` (from Pydantic) and represents the configuration for a single application.

##### Methods

```python
def get_app_name(self) -> str: ...
```

- **get_app_name**: Returns the name of the application.

```python
def get_app_label(self) -> str:...
```

- **get_app_label**: Returns the label of the application, if it exists.

```python
def get_verbose_name(self) -> str: ...
```
- **get_verbose_name**: Returns the verbose name of the application.

```python
def get_model(self, name: str) -> type[edgy.Model]: ...
```

- **get_model**: Returns a specific model by its name. Raises an exception if the model is not found.

```python
def get_models(self) -> dict[str, type[edgy.Model]]: ...
```
- **get_models**: Returns all models associated with the application. It imports the module containing the models and filters them based on specific conditions.

#### Apps Class

```python
class Apps: ...
```

- **Apps**: This class manages the registry of all applications within the larger application framework.

##### Methods

```python
def get_app_configs(self) -> dict[str, AppConfig]: ...
```

- **get_app_configs**: Returns the configurations of all registered applications.

```python
def get_app_config(self, app_label: str) -> AppConfig: ...
```

- **get_app_config**: Returns the configuration for a specific application by its **name**. Raises an exception if the application is not found.

```python
def get_models(self) -> list[type[edgy.Model]]: ...
```

- **get_models**: Returns all models from the registry.

```python
def get_model(self, app_label: str, model_name: str) -> type[edgy.Model]: ...
```

- **get_model**: Returns a specific model from the registry of the application configuration.

#### Singleton Instance and Caching

```python
apps = Apps()

@lru_cache
def get_apps() -> Apps:
    return apps
```

- **Singleton Instance**: Creates a singleton instance of the `Apps` class.
- **Caching**: Uses `lru_cache` to cache the `get_apps` function, ensuring that the same instance is returned on subsequent calls.

