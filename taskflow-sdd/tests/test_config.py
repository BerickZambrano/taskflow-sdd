import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/db"
    )
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    settings = Settings()
    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/db"
    assert settings.secret_key == "test-secret"
    assert settings.access_token_expire_minutes == 1440


def test_settings_requires_mandatory_variables(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings()
