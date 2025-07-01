# Release Notes

## 0.4.0

### Added

* Added `get_obj_perms` shortcut to asynchronously retrieve all permissions a user holds on a given object, with support for Django-style filter kwargs.
* Updated documentation and examples in `shortcuts` to include usage patterns and parameter details for `get_obj_perms`.

## 0.3.0

### Changed

- Removed `from __future__ import annotations` as the minimum version of Python is 3.10.
- Add minimum version of `edgy` to be 0.31.0.

## 0.2.0

### Added

- [Managers](./managers.md) documentation section.
- Allow passing objects for permissions and groups in `has_user_perm` and `has_group_permission`.

### Changed

- Rename internal models manager default from `query` to `guardian`. This will avoid any clash or
the existing `query` override in any edgy models.

### Fixed

- Unnecessary load of apps for ContentTypes.
- Mandatory obj attribute in `assign_perm`.
- Mypy typing and checks.

## 0.1.0

### Added

- First official release of Edgy Guardian
- [Quickstart](./index.md) guide.
- [Tutorial](./simple-how-to.md)
- [Shortcuts](./shortcuts.md)
- [Mixins](./mixins.md)
