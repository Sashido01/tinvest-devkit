from __future__ import annotations

import argparse
from pathlib import Path

from tinvest_devkit.bootstrap import (
    bootstrap_project,
)
from tinvest_devkit.doctor import (
    main as doctor_main,
)
from tinvest_devkit.scaffold import (
    scaffold_project,
)


def _resolve_devkit_root() -> Path:
    return (
        Path(__file__)
        .resolve()
        .parents[2]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tinvest-devkit",
        description=(
            "Reusable read-only development tools "
            "for T-Invest API projects"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help=(
            "check environment and "
            "T-Invest API readiness"
        ),
    )

    doctor_parser.add_argument(
        "--env",
        default=".env",
        help=(
            "path to environment file "
            "(default: .env)"
        ),
    )

    new_parser = subparsers.add_parser(
        "new",
        help=(
            "create and bootstrap "
            "a new T-Invest project"
        ),
    )

    new_parser.add_argument(
        "project_name",
        help="new project name",
    )

    new_parser.add_argument(
        "--destination",
        default=".",
        help=(
            "parent directory for the "
            "new project "
            "(default: current directory)"
        ),
    )

    new_parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help=(
            "create project files only "
            "without virtual environment, "
            "dependencies or Git initialization"
        ),
    )

    new_parser.add_argument(
        "--no-git",
        action="store_true",
        help=(
            "bootstrap environment "
            "without Git initialization"
        ),
    )

    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(
        argv
    )

    if args.command == "doctor":
        return doctor_main(
            env_path=args.env
        )

    if args.command == "new":
        try:
            result = scaffold_project(
                args.project_name,
                destination=Path(
                    args.destination
                ),
            )
        except (
            ValueError,
            FileExistsError,
            OSError,
        ) as error:
            print(
                f"ERROR: {error}"
            )
            return 1

        print(
            "Project created:"
        )
        print(
            result.project_path
        )
        print()
        print(
            f"Package: {result.package_name}"
        )
        print(
            f"Files: {len(result.created_files)}"
        )

        if args.no_bootstrap:
            print()
            print(
                "Bootstrap skipped."
            )
            return 0

        try:
            bootstrap_result = (
                bootstrap_project(
                    result.project_path,
                    _resolve_devkit_root(),
                    initialize_git=(
                        not args.no_git
                    ),
                )
            )
        except Exception as error:
            print()
            print(
                "ERROR: bootstrap failed:"
            )
            print(
                f"{type(error).__name__}: "
                f"{error}"
            )
            return 1

        print()
        print(
            "Environment ready:"
        )
        print(
            bootstrap_result.venv_python
        )

        print()
        print(
            "Next steps:"
        )
        print(
            "1. Copy .env.example to .env"
        )
        print(
            "2. Set TINVEST_TOKEN"
        )
        print(
            "3. Set TINVEST_ACCOUNT_ID if needed"
        )
        print(
            "4. Run tinvest-devkit doctor --env .env"
        )

        return 0

    parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
