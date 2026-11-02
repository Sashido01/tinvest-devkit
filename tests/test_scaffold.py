import pytest

from tinvest_devkit.__main__ import main
from tinvest_devkit.scaffold import (
    normalize_package_name,
    scaffold_project,
    validate_project_name,
)


def test_normalize_package_name() -> None:
    assert (
        normalize_package_name(
            "My-Invest_Project"
        )
        == "my_invest_project"
    )


@pytest.mark.parametrize(
    "project_name",
    [
        "",
        "bad name",
        "-project",
        "_project",
        "project!",
        "project/path",
    ],
)
def test_invalid_project_names_are_rejected(
    project_name,
) -> None:
    with pytest.raises(ValueError):
        validate_project_name(
            project_name
        )


def test_scaffold_creates_expected_structure(
    tmp_path,
) -> None:
    result = scaffold_project(
        "MyProject",
        destination=tmp_path,
    )

    project = (
        tmp_path
        / "MyProject"
    )

    assert result.project_path == (
        project.resolve()
    )

    assert result.package_name == (
        "myproject"
    )

    expected_files = (
        ".env.example",
        ".gitignore",
        ".gitattributes",
        "pyproject.toml",
        "pytest.ini",
        "README.md",
        "docs/ARCHITECTURE.md",
        "src/myproject/__init__.py",
        "src/myproject/main.py",
        "tests/__init__.py",
        "tests/test_smoke.py",
    )

    for relative_path in expected_files:
        assert (
            project
            / relative_path
        ).is_file()


def test_scaffold_uses_devkit_dependency(
    tmp_path,
) -> None:
    result = scaffold_project(
        "Demo-Invest",
        destination=tmp_path,
    )

    pyproject = (
        result.project_path
        / "pyproject.toml"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        'tinvest-devkit>=0.1.0'
        in pyproject
    )

    main_file = (
        result.project_path
        / "src"
        / "demo_invest"
        / "main.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "TInvestReadClient"
        in main_file
    )

    assert (
        "load_settings"
        in main_file
    )


def test_scaffold_does_not_create_real_env(
    tmp_path,
) -> None:
    result = scaffold_project(
        "DemoProject",
        destination=tmp_path,
    )

    assert not (
        result.project_path
        / ".env"
    ).exists()

    assert (
        result.project_path
        / ".env.example"
    ).is_file()


def test_scaffold_refuses_existing_target(
    tmp_path,
) -> None:
    target = (
        tmp_path
        / "ExistingProject"
    )

    target.mkdir()

    with pytest.raises(
        FileExistsError
    ):
        scaffold_project(
            "ExistingProject",
            destination=tmp_path,
        )


def test_cli_new_creates_project(
    tmp_path,
    capsys,
) -> None:
    exit_code = main(
        [
            "new",
            "CliProject",
            "--destination",
            str(tmp_path),
            "--no-bootstrap",
        ]
    )

    assert exit_code == 0

    assert (
        tmp_path
        / "CliProject"
        / "src"
        / "cliproject"
        / "main.py"
    ).is_file()

    output = (
        capsys
        .readouterr()
        .out
    )

    assert (
        "Project created:"
        in output
    )

    assert (
        "Package: cliproject"
        in output
    )


def test_cli_new_returns_error_for_existing_target(
    tmp_path,
    capsys,
) -> None:
    target = (
        tmp_path
        / "ExistingProject"
    )

    target.mkdir()

    exit_code = main(
        [
            "new",
            "ExistingProject",
            "--destination",
            str(tmp_path),
        ]
    )

    assert exit_code == 1

    output = (
        capsys
        .readouterr()
        .out
    )

    assert "ERROR:" in output


def test_generated_text_files_use_lf(
    tmp_path,
) -> None:
    result = scaffold_project(
        "LineEndingProject",
        destination=tmp_path,
    )

    for file_path in result.created_files:
        data = file_path.read_bytes()

        assert b"\r\n" not in data

def test_cli_new_bootstraps_project(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    calls = []

    def fake_bootstrap(
        project_path,
        devkit_path,
        *,
        initialize_git=True,
    ):
        calls.append(
            (
                project_path,
                devkit_path,
                initialize_git,
            )
        )

        return type(
            "BootstrapResult",
            (),
            {
                "venv_python": (
                    project_path
                    / ".venv"
                    / "Scripts"
                    / "python.exe"
                )
            },
        )()

    monkeypatch.setattr(
        "tinvest_devkit.__main__.bootstrap_project",
        fake_bootstrap,
    )

    exit_code = main(
        [
            "new",
            "BootstrapProject",
            "--destination",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert len(calls) == 1

    project_path = (
        tmp_path
        / "BootstrapProject"
    ).resolve()

    assert calls[0][0] == project_path
    assert calls[0][2] is True

    output = (
        capsys
        .readouterr()
        .out
    )

    assert "Environment ready:" in output
    assert "Next steps:" in output


def test_cli_new_no_git_passes_false(
    tmp_path,
    monkeypatch,
) -> None:
    calls = []

    def fake_bootstrap(
        project_path,
        devkit_path,
        *,
        initialize_git=True,
    ):
        calls.append(
            initialize_git
        )

        return type(
            "BootstrapResult",
            (),
            {
                "venv_python": (
                    project_path
                    / ".venv"
                    / "Scripts"
                    / "python.exe"
                )
            },
        )()

    monkeypatch.setattr(
        "tinvest_devkit.__main__.bootstrap_project",
        fake_bootstrap,
    )

    exit_code = main(
        [
            "new",
            "NoGitProject",
            "--destination",
            str(tmp_path),
            "--no-git",
        ]
    )

    assert exit_code == 0
    assert calls == [False]


def test_cli_new_no_bootstrap_skips_bootstrap(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    called = False

    def fake_bootstrap(
        project_path,
        devkit_path,
        *,
        initialize_git=True,
    ):
        nonlocal called
        called = True

        raise AssertionError(
            "bootstrap must not be called"
        )

    monkeypatch.setattr(
        "tinvest_devkit.__main__.bootstrap_project",
        fake_bootstrap,
    )

    exit_code = main(
        [
            "new",
            "ScaffoldOnlyProject",
            "--destination",
            str(tmp_path),
            "--no-bootstrap",
        ]
    )

    assert exit_code == 0
    assert called is False

    output = (
        capsys
        .readouterr()
        .out
    )

    assert "Bootstrap skipped." in output


def test_cli_new_reports_bootstrap_failure(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    def fake_bootstrap(
        project_path,
        devkit_path,
        *,
        initialize_git=True,
    ):
        raise RuntimeError(
            "bootstrap exploded"
        )

    monkeypatch.setattr(
        "tinvest_devkit.__main__.bootstrap_project",
        fake_bootstrap,
    )

    exit_code = main(
        [
            "new",
            "BrokenBootstrapProject",
            "--destination",
            str(tmp_path),
        ]
    )

    assert exit_code == 1

    output = (
        capsys
        .readouterr()
        .out
    )

    assert (
        "ERROR: bootstrap failed:"
        in output
    )

    assert (
        "RuntimeError: bootstrap exploded"
        in output
    )
