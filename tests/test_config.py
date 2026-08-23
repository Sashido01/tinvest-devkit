import pytest

from tinvest_devkit.config import load_settings


def test_load_settings_from_env_file(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "TINVEST_TOKEN",
        raising=False,
    )
    monkeypatch.delenv(
        "TINVEST_ACCOUNT_ID",
        raising=False,
    )

    env_file = tmp_path / ".env"

    env_file.write_text(
        "TINVEST_TOKEN=test-token\n"
        "TINVEST_ACCOUNT_ID=test-account\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.token == "test-token"
    assert settings.account_id == "test-account"


def test_account_id_is_optional(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "TINVEST_TOKEN",
        raising=False,
    )
    monkeypatch.delenv(
        "TINVEST_ACCOUNT_ID",
        raising=False,
    )

    env_file = tmp_path / ".env"

    env_file.write_text(
        "TINVEST_TOKEN=test-token\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.token == "test-token"
    assert settings.account_id is None


def test_account_id_can_be_required(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "TINVEST_TOKEN",
        raising=False,
    )
    monkeypatch.delenv(
        "TINVEST_ACCOUNT_ID",
        raising=False,
    )

    env_file = tmp_path / ".env"

    env_file.write_text(
        "TINVEST_TOKEN=test-token\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="TINVEST_ACCOUNT_ID is required",
    ):
        load_settings(
            env_file,
            require_account_id=True,
        )


def test_missing_token_is_rejected(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "TINVEST_TOKEN",
        raising=False,
    )
    monkeypatch.delenv(
        "TINVEST_ACCOUNT_ID",
        raising=False,
    )

    env_file = tmp_path / ".env"
    env_file.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="TINVEST_TOKEN is required",
    ):
        load_settings(env_file)


def test_environment_overrides_env_file(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "TINVEST_TOKEN",
        "environment-token",
    )
    monkeypatch.setenv(
        "TINVEST_ACCOUNT_ID",
        "environment-account",
    )

    env_file = tmp_path / ".env"

    env_file.write_text(
        "TINVEST_TOKEN=file-token\n"
        "TINVEST_ACCOUNT_ID=file-account\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.token == "environment-token"
    assert settings.account_id == "environment-account"
