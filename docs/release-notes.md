# Release Notes

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
