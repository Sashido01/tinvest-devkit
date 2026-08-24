from __future__ import annotations

import argparse

from tinvest_devkit.doctor import (
    main as doctor_main,
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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "doctor":
        return doctor_main(
            env_path=args.env
        )

    parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
