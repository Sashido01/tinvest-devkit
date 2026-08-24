from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


TBANK_INDEX_URL = (
    "https://opensource.tbank.ru/api/v4/"
    "projects/238/packages/pypi/simple"
)


@dataclass(frozen=True)
class BootstrapCommand:
    args: tuple[str, ...]
    cwd: Path


@dataclass(frozen=True)
class BootstrapResult:
    project_path: Path
    venv_python: Path
    commands: tuple[BootstrapCommand, ...]


CommandRunner = Callable[
    [Sequence[str], Path],
    None,
]


def _default_runner(
    args: Sequence[str],
    cwd: Path,
) -> None:
    subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
    )


def resolve_venv_python(
    project_path: str | Path,
) -> Path:
    project = Path(
        project_path
    ).resolve()

    if sys.platform == "win32":
        return (
            project
            / ".venv"
            / "Scripts"
            / "python.exe"
        )

    return (
        project
        / ".venv"
        / "bin"
        / "python"
    )


def validate_bootstrap_paths(
    project_path: str | Path,
    devkit_path: str | Path,
) -> tuple[Path, Path]:
    project = Path(
        project_path
    ).resolve()

    devkit = Path(
        devkit_path
    ).resolve()

    if not project.is_dir():
        raise FileNotFoundError(
            f"project directory not found: {project}"
        )

    if not (
        project
        / "pyproject.toml"
    ).is_file():
        raise FileNotFoundError(
            "generated project pyproject.toml "
            f"not found: {project}"
        )

    if not devkit.is_dir():
        raise FileNotFoundError(
            f"devkit directory not found: {devkit}"
        )

    if not (
        devkit
        / "pyproject.toml"
    ).is_file():
        raise FileNotFoundError(
            "tinvest-devkit pyproject.toml "
            f"not found: {devkit}"
        )

    requirements = (
        devkit
        / "requirements.txt"
    )

    if not requirements.is_file():
        raise FileNotFoundError(
            "tinvest-devkit requirements.txt "
            f"not found: {requirements}"
        )

    return project, devkit


def build_bootstrap_commands(
    project_path: str | Path,
    devkit_path: str | Path,
    *,
    host_python: str | Path | None = None,
    initialize_git: bool = True,
) -> tuple[BootstrapCommand, ...]:
    project, devkit = (
        validate_bootstrap_paths(
            project_path,
            devkit_path,
        )
    )

    host_python_path = str(
        host_python
        if host_python is not None
        else sys.executable
    )

    venv_python = resolve_venv_python(
        project
    )

    commands: list[
        BootstrapCommand
    ] = [
        BootstrapCommand(
            args=(
                host_python_path,
                "-m",
                "venv",
                ".venv",
            ),
            cwd=project,
        ),
        BootstrapCommand(
            args=(
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ),
            cwd=project,
        ),
        BootstrapCommand(
            args=(
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-r",
                str(
                    devkit
                    / "requirements.txt"
                ),
            ),
            cwd=project,
        ),
        BootstrapCommand(
            args=(
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-e",
                str(devkit),
                "--no-deps",
            ),
            cwd=project,
        ),
        BootstrapCommand(
            args=(
                str(venv_python),
                "-m",
                "pip",
                "install",
                "pytest==9.1.1",
            ),
            cwd=project,
        ),
        BootstrapCommand(
            args=(
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-e",
                ".",
                "--no-deps",
            ),
            cwd=project,
        ),
    ]

    if initialize_git:
        commands.extend(
            [
                BootstrapCommand(
                    args=(
                        "git",
                        "init",
                    ),
                    cwd=project,
                ),
                BootstrapCommand(
                    args=(
                        "git",
                        "branch",
                        "-M",
                        "main",
                    ),
                    cwd=project,
                ),
            ]
        )

    commands.extend(
        [
            BootstrapCommand(
                args=(
                    str(venv_python),
                    "-m",
                    "pytest",
                ),
                cwd=project,
            ),
            BootstrapCommand(
                args=(
                    str(venv_python),
                    "-m",
                    "compileall",
                    "-q",
                    "src",
                    "tests",
                ),
                cwd=project,
            ),
        ]
    )

    return tuple(commands)


def bootstrap_project(
    project_path: str | Path,
    devkit_path: str | Path,
    *,
    host_python: str | Path | None = None,
    initialize_git: bool = True,
    runner: CommandRunner = _default_runner,
) -> BootstrapResult:
    project, _ = validate_bootstrap_paths(
        project_path,
        devkit_path,
    )

    commands = build_bootstrap_commands(
        project_path,
        devkit_path,
        host_python=host_python,
        initialize_git=initialize_git,
    )

    for command in commands:
        runner(
            command.args,
            command.cwd,
        )

    return BootstrapResult(
        project_path=project,
        venv_python=resolve_venv_python(
            project
        ),
        commands=commands,
    )
