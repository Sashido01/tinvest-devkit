from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    token: str
    account_id: str | None = None


def load_env_file(path: str | Path = ".env") -> None:
    env_path = Path(path)

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(
        encoding="utf-8-sig"
    ).splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        if key and key not in os.environ:
            os.environ[key] = value


def load_settings(
    env_path: str | Path = ".env",
    *,
    require_account_id: bool = False,
) -> Settings:
    load_env_file(env_path)

    token = os.getenv(
        "TINVEST_TOKEN",
        "",
    ).strip()

    account_id = os.getenv(
        "TINVEST_ACCOUNT_ID",
        "",
    ).strip()

    if not token:
        raise ValueError(
            "TINVEST_TOKEN is required"
        )

    if require_account_id and not account_id:
        raise ValueError(
            "TINVEST_ACCOUNT_ID is required"
        )

    return Settings(
        token=token,
        account_id=account_id or None,
    )
