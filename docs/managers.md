# Introducing the `guardian` Manager

Edgy Guardian introduces a new manager called `guardian` to provide a safer approach to querying models while avoiding unintended overrides that may occur when using the default `query` manager.

## Why `guardian`?

In traditional Edgy usage, the `query` manager is used for all model-related database operations. However, this approach can sometimes lead to accidental overrides, especially when dealing with multiple models sharing similar query structures.

To prevent this issue, Edgy Guardian introduces `guardian`, a new manager that ensures model safety by isolating its operations from `query`. This allows developers to perform safe database queries without interfering with existing model configurations.

## How to Use `guardian`

The `guardian` manager is available on all Edgy Guardian models and can be used as follows:

```python
from edgy_guardian.permissions.models import BasePermission

class Permission(BasePermission): ...

# Using guardian for queries
perms = Permission.guardian.all()
```

By using `guardian`, developers can safely query models without modifying or overriding any existing operations associated with `query`.

!!! Tip
    **You can create your own manager and also call it `guardian` in your models**. Edgy Guardian only
    introduces this for the custom library models and avoid clashing.

## Key Benefits

- **Prevents Unintended Overrides**: Ensures that model queries do not conflict with the default `query` manager.
- **Safe Querying**: Allows developers to execute database operations in a controlled environment.
- **Enhanced Maintainability**: Reduces potential errors in large codebases by providing an alternative query manager.

## Conclusion

The introduction of `guardian` in Edgy Guardian enhances model safety and query integrity. By using `guardian`, developers can avoid accidental modifications and maintain cleaner, more predictable database interactions.
