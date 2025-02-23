from edgy import EdgySettings


class TestSettings(EdgySettings):
    guardian_user_model: str = "tests.models.User"
    guardian_group_model: str = "tests.models.Group"
    guardian_permission_model: str = "tests.models.Permission"
