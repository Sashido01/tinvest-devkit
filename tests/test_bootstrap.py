from pathlib import Path

import pytest

from tinvest_devkit.bootstrap import (
    TBANK_INDEX_URL,
    bootstrap_project,
    build_bootstrap_commands,
    resolve_venv_python,
    validate_bootstrap_paths,
)


def make_project(
    root: Path,
) -> Path:
    project = root / "DemoProject"
    project.mkdir()

    (
        project
        / "pyproject.toml"
    ).write_text(
        "[project]\n"
        'name = "demo-project"\n'
        'version = "0.1.0"\n',
        encoding="utf-8",
    )

    return project


def make_devkit(
    root: Path,
) -> Path:
    devkit = root / "tinvest-devkit"
    devkit.mkdir()

    (
        devkit
        / "pyproject.toml"
    ).write_text(
        "[project]\n"
        'name = "tinvest-devkit"\n'
        'version = "0.1.0"\n',
        encoding="utf-8",
    )

    (
        devkit
        / "requirements.txt"
    ).write_text(
        "--index-url "
        + TBANK_INDEX_URL
        + "\n"
        + "t-tech-investments==1.49.3\n",
        encoding="utf-8",
    )

    return devkit


def test_validate_bootstrap_paths(
    tmp_path,
) -> None:
    project = make_project(
        tmp_path
    )
    devkit = make_devkit(
        tmp_path
    )

    resolved_project, resolved_devkit = (
        validate_bootstrap_paths(
            project,
            devkit,
        )
    )

    assert (
        resolved_project
        == project.resolve()
    )

    assert (
        resolved_devkit
        == devkit.resolve()
    )


def test_missing_project_is_rejected(
    tmp_path,
) -> None:
    devkit = make_devkit(
        tmp_path
    )

    with pytest.raises(
        FileNotFoundError,
        match="project directory not found",
    ):
        validate_bootstrap_paths(
            tmp_path / "missing",
            devkit,
        )


def test_missing_project_pyproject_is_rejected(
    tmp_path,
) -> None:
    project = (
        tmp_path
        / "project"
    )
    project.mkdir()

    devkit = make_devkit(
        tmp_path
    )

    with pytest.raises(
        FileNotFoundError,
        match=(
            "generated project "
            "pyproject.toml not found"
        ),
    ):
        validate_bootstrap_paths(
            project,
            devkit,
        )


def test_missing_devkit_is_rejected(
    tmp_path,
) -> None:
    project = make_project(
        tmp_path
    )

    with pytest.raises(
        FileNotFoundError,
        match="devkit directory not found",
    ):
        validate_bootstrap_paths(
            project,
            tmp_path / "missing",
        )


def test_missing_devkit_requirements_is_rejected(
    tmp_path,
) -> None:
    project = make_project(
        tmp_path
    )

    devkit = (
        tmp_path
        / "devkit"
    )
    devkit.mkdir()

    (
        devkit
        / "pyproject.toml"
    ).write_text(
        "[project]\n"
        'name = "tinvest-devkit"\n',
        encoding="utf-8",
    )

    with pytest.raises(
        FileNotFoundError,
        match=(
            "tinvest-devkit "
            "requirements.txt not found"
        ),
    ):
        validate_bootstrap_paths(
            project,
            devkit,
        )


def test_resolve_venv_python(
    tmp_path,
    monkeypatch,
) -> None:
    project = (
        tmp_path
        / "project"
    )

    monkeypatch.setattr(
        "tinvest_devkit.bootstrap.sys.platform",
        "win32",
    )

    result = resolve_venv_python(
        project
    )

    assert result == (
        project.resolve()
        / ".venv"
        / "Scripts"
        / "python.exe"
    )


def test_build_bootstrap_commands(
    tmp_path,
    monkeypatch,
) -> None:
    project = make_project(
        tmp_path
    )
    devkit = make_devkit(
        tmp_path
    )

    monkeypatch.setattr(
        "tinvest_devkit.bootstrap.sys.platform",
        "win32",
    )

    commands = build_bootstrap_commands(
        project,
        devkit,
        host_python="C:/Python311/python.exe",
    )

    assert len(commands) == 10

    assert commands[0].args == (
        "C:/Python311/python.exe",
        "-m",
        "venv",
        ".venv",
    )

    venv_python = str(
        project.resolve()
        / ".venv"
        / "Scripts"
        / "python.exe"
    )

    assert commands[1].args == (
        venv_python,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
    )

    assert commands[2].args == (
        venv_python,
        "-m",
        "pip",
        "install",
        "-r",
        str(
            devkit.resolve()
            / "requirements.txt"
        ),
    )

    assert commands[3].args == (
        venv_python,
        "-m",
        "pip",
        "install",
        "-e",
        str(
            devkit.resolve()
        ),
        "--no-deps",
    )

    assert commands[4].args == (
        venv_python,
        "-m",
        "pip",
        "install",
        "pytest==9.1.1",
    )

    assert commands[5].args == (
        venv_python,
        "-m",
        "pip",
        "install",
        "-e",
        ".",
        "--no-deps",
    )

    assert commands[6].args == (
        "git",
        "init",
    )

    assert commands[7].args == (
        "git",
        "branch",
        "-M",
        "main",
    )

    assert commands[8].args == (
        venv_python,
        "-m",
        "pytest",
    )

    assert commands[9].args == (
        venv_python,
        "-m",
        "compileall",
        "-q",
        "src",
        "tests",
    )

    assert all(
        command.cwd
        == project.resolve()
        for command
        in commands
    )


def test_build_bootstrap_commands_without_git(
    tmp_path,
    monkeypatch,
) -> None:
    project = make_project(
        tmp_path
    )
    devkit = make_devkit(
        tmp_path
    )

    monkeypatch.setattr(
        "tinvest_devkit.bootstrap.sys.platform",
        "win32",
    )

    commands = build_bootstrap_commands(
        project,
        devkit,
        initialize_git=False,
    )

    args = [
        command.args
        for command in commands
    ]

    assert (
        "git",
        "init",
    ) not in args

    assert (
        "git",
        "branch",
        "-M",
        "main",
    ) not in args

    assert len(commands) == 8


def test_bootstrap_project_executes_commands(
    tmp_path,
    monkeypatch,
) -> None:
    project = make_project(
        tmp_path
    )
    devkit = make_devkit(
        tmp_path
    )

    monkeypatch.setattr(
        "tinvest_devkit.bootstrap.sys.platform",
        "win32",
    )

    calls = []

    def fake_runner(
        args,
        cwd,
    ) -> None:
        calls.append(
            (
                tuple(args),
                cwd,
            )
        )

    result = bootstrap_project(
        project,
        devkit,
        host_python="C:/Python311/python.exe",
        runner=fake_runner,
    )

    assert len(result.commands) == 10
    assert len(calls) == 10

    assert result.project_path == (
        project.resolve()
    )

    assert result.venv_python == (
        project.resolve()
        / ".venv"
        / "Scripts"
        / "python.exe"
    )

    assert calls == [
        (
            command.args,
            command.cwd,
        )
        for command
        in result.commands
    ]
