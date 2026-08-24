from __future__ import annotations

import argparse
from pathlib import Path

from tinvest_devkit.doctor import (
    main as doctor_main,
)
from tinvest_devkit.scaffold import (
    scaffold_project,
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
            "create a new T-Invest project"
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
        print()
        print(
            "Next step: bootstrap the "
            "project environment."
        )

        return 0

    parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
