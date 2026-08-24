from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path


PROJECT_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
)


@dataclass(frozen=True)
class ScaffoldResult:
    project_name: str
    package_name: str
    project_path: Path
    created_files: tuple[Path, ...]


def normalize_package_name(
    project_name: str,
) -> str:
    return project_name.lower().replace(
        "-",
        "_",
    )


def validate_project_name(
    project_name: str,
) -> None:
    if not project_name:
        raise ValueError(
            "project_name is required"
        )

    if not PROJECT_NAME_PATTERN.fullmatch(
        project_name
    ):
        raise ValueError(
            "project_name may contain only "
            "letters, digits, hyphens and underscores "
            "and must start with a letter or digit"
        )


def _write_text(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content.strip() + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _project_files(
    *,
    project_name: str,
    package_name: str,
) -> dict[str, str]:
    return {
        ".env.example": (
            "TINVEST_TOKEN=\n"
            "TINVEST_ACCOUNT_ID=\n"
        ),
        ".gitignore": """
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.pyo
*.sqlite3
*.db
dist/
build/
*.egg-info/
""",
        ".gitattributes": """
* text=auto

*.py   text eol=lf
*.md   text eol=lf
*.html text eol=lf
*.css  text eol=lf
*.ini  text eol=lf
*.txt  text eol=lf
*.json text eol=lf
*.yml  text eol=lf
*.yaml text eol=lf
*.toml text eol=lf

*.cmd  text eol=crlf
*.bat  text eol=crlf
*.ps1  text eol=crlf

*.sqlite3 binary
*.db      binary
*.png     binary
*.jpg     binary
*.jpeg    binary
*.gif     binary
*.ico     binary
""",
        "pyproject.toml": f"""
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name.lower()}"
version = "0.1.0"
description = "T-Invest project generated with tinvest-devkit"
requires-python = ">=3.11"

dependencies = [
    "tinvest-devkit>=0.1.0",
]

[tool.setuptools.packages.find]
where = ["src"]
""",
        "pytest.ini": """
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra
""",
        "README.md": f"""
# {project_name}

T-Invest project generated with tinvest-devkit.

## Configuration

Create `.env` from `.env.example`.

Required configuration:

TINVEST_TOKEN=

Optional account selection:

TINVEST_ACCOUNT_ID=

Never commit the real `.env` file.

## Starter

The generated application uses:

- `TInvestReadClient`;
- `load_settings`;
- read-only T-Invest access;
- pytest;
- src-layout.

Environment creation and dependency installation are handled by
the bootstrap stage of tinvest-devkit.
""",
        "docs/ARCHITECTURE.md": f"""
# {project_name} - architecture

The generated project keeps T-Invest SDK-specific integration
behind tinvest-devkit.

Data flow:

T-Invest API
-> tinvest-devkit
-> application code

Application-specific accounting, storage, analytics, strategies
and interfaces belong to this project.
""",
        f"src/{package_name}/__init__.py": (
            f'"""{project_name} application package."""\n'
        ),
        f"src/{package_name}/main.py": """
from __future__ import annotations

from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import load_settings


def main() -> None:
    settings = load_settings()
    client = TInvestReadClient(
        settings
    )

    accounts = client.get_accounts()

    print(
        "T-Invest connection OK. "
        f"Accounts available: {len(accounts)}"
    )


if __name__ == "__main__":
    main()
""",
        "tests/__init__.py": "",
        "tests/test_smoke.py": f"""
import {package_name}.main


def test_application_module_imports() -> None:
    assert {package_name}.main is not None
""",
    }


def scaffold_project(
    project_name: str,
    *,
    destination: str | Path = ".",
) -> ScaffoldResult:
    validate_project_name(
        project_name
    )

    package_name = normalize_package_name(
        project_name
    )

    destination_path = Path(
        destination
    ).expanduser().resolve()

    project_path = (
        destination_path
        / project_name
    )

    if project_path.exists():
        raise FileExistsError(
            f"target already exists: {project_path}"
        )

    project_path.mkdir(
        parents=True,
        exist_ok=False,
    )

    files = _project_files(
        project_name=project_name,
        package_name=package_name,
    )

    created_files: list[Path] = []

    try:
        for relative_path, content in files.items():
            file_path = (
                project_path
                / relative_path
            )

            _write_text(
                file_path,
                content,
            )

            created_files.append(
                file_path
            )
    except Exception:
        shutil.rmtree(
            project_path,
            ignore_errors=True,
        )
        raise

    return ScaffoldResult(
        project_name=project_name,
        package_name=package_name,
        project_path=project_path,
        created_files=tuple(
            created_files
        ),
    )
