# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

"""
This is a sample Python CLI script.  Set up command line arguments in a class derived from ApplicationSettings.

You need to update the following class variables in Settings class to match your needs:

* project_name
* project_package
* project_description

and then add any arguments to Settings.add_arguments() and Settings.validate_arguments() methods.

Finally, add your application into the main() method.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from version_bumper.clibones.application_settings import ApplicationSettings
from version_bumper.commands import bump_command, get_command, release_command, set_command, version_command
from version_bumper.version import Version

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence


# noinspection PyMethodMayBeStatic
class Settings(ApplicationSettings):
    """Where the project's initial state (i.e. settings) are defined.

    Settings extends the generic ApplicationSettings class which parses the command line arguments.

    Usage::

        with Settings() as settings:
        try:
            app.execute(settings)
            exit(0)
        except ArgumentError as ex:
            error(str(ex))
            exit(1)
    """

    __project_name: str = "Version Bumper"
    """The name of the project"""

    __project_package: str = "version_bumper"
    """The name of the package this settings belongs to. """

    __project_description: str = (
        "Python package version utility to bump a version by parts: "
        "[N!]N(.N)*[{a|b|rc}N][.postN][.devN][+N] "
        "or with part names in lowercase: "
        "[epoch!]major[.minor[.patch]][a|b|rc][.post][.dev][+local]"
    )
    """A short description of the application."""

    def __init__(self, args: Sequence[str] | None = None) -> None:
        """Initialize the base class."""

        super().__init__(
            app_name=Settings.__project_name,
            app_package=Settings.__project_package,
            app_description=Settings.__project_description,
            config_sections=[Settings.__project_package],
            args=args,
        )
        self.add_persist_keys({"pyproject_toml_path", "loglevel", "debug"})

    def add_parent_parsers(self) -> list[argparse.ArgumentParser]:
        """This is where you should add any parent parsers for the main parser.

        :return: a list of parent parsers
        """
        return []

    def add_arguments(self, parser: argparse.ArgumentParser, defaults: dict[str, str]) -> None:  # noqa: ARG002
        """This is where you should add arguments to the parser.

        To add application arguments, you should override this method.

        :param parser: the argument parser with --conf_file already added.
        :param defaults: the default dictionary usually loaded from a config file
        """
        # use normal argparse commands to add arguments to the given parser.  Example:

        def add_common_arguments(parser: argparse.ArgumentParser) -> None:
            """
            Add these arguments to the given parser.
            """
            parser.add_argument(
                "--pyproject",
                dest="pyproject_toml_path",
                default=pyproject_toml_path,
                type=Path,
                action="store",
                help="pyproject.toml file update the version within.",
            )

        pyproject_toml_path = Path(__file__).parent.parent.parent.joinpath("pyproject.toml").resolve()

        subparsers = parser.add_subparsers(dest="command")

        bump_parser = subparsers.add_parser(
            "bump", description="Bump the given part of the current version in the " "pyproject.toml file."
        )
        bump_parser.add_argument("part", choices=Version.PARTS, help="Bump this part of the current version")
        bump_parser.add_argument(
            "--json", action="store_true", help='Input is JSON string containing the part name to increment, ex: "dev"'
        )
        bump_parser.add_argument("--text", action="store_true", help='Input is text string, ex: "1.2.3rc1-dev3"')
        add_common_arguments(bump_parser)

        version_parser = subparsers.add_parser(
            "version", description="Set the current version in the pyproject.toml file."
        )
        version_parser.add_argument("value", nargs="?", default="", type=str, help="Set the version to this value.")
        version_parser.add_argument("--json", action="store_true", help='Input is JSON string, ex: "1.2.3rc1-dev3"')
        version_parser.add_argument("--text", action="store_true", help='Input is text string, ex: "1.2.3rc1-dev3"')
        version_parser.add_argument("--silent", action="store_true", help="Silence output (used for tests)")
        add_common_arguments(version_parser)

        set_parser = subparsers.add_parser(
            "set", description="Set part of the current version in the pyproject.toml file " "to the given value."
        )
        set_parser.add_argument("part", choices=Version.PARTS, help="Set this part of the current version.")
        set_parser.add_argument("value", nargs="?", default="", type=str, help="Set the version part to this value.")
        set_parser.add_argument(
            "--clear_right",
            action="store_true",
            help="Clear the parts of the current version to the right of the part.",
        )
        set_parser.add_argument("--json", action="store_true", help='Input is JSON dictionary, ex: "{"rc": "1"}"')
        set_parser.add_argument("--text", action="store_true", help='Input is text, ex: "rc1"')
        add_common_arguments(set_parser)

        get_parser = subparsers.add_parser("get", description="Get the current version from the pyproject.toml file.")
        get_parser.add_argument("--project", action="store_true", help="Get the project.version value.")
        get_parser.add_argument("--poetry", action="store_true", help="Get the tool.poetry.version value.")
        get_parser.add_argument(
            "--all", action="store_true", help="Get both project.version and tool.poetry.version values. [Default]"
        )
        get_parser.add_argument("--json", action="store_true", help='Output as JSON string, ex: "1.2.3rc1-dev"')
        get_parser.add_argument("--text", action="store_true", help='Output as text string, ex: "1.2.3rc1-dev"')
        add_common_arguments(get_parser)

        release_parser = subparsers.add_parser(
            "release", description="Change version to a release version, i.e. [N!]N[.N[.N]]"
        )
        release_parser.add_argument("--json", action="store_true", help='Output as JSON string, ex: "1.2.3"')
        release_parser.add_argument("--text", action="store_true", help='Output as text string, ex: "1.2.3"')
        add_common_arguments(release_parser)

    def validate_arguments(self, settings: argparse.Namespace, remaining_argv: list[str]) -> list[str]:  # noqa: ARG002
        """This provides a hook for validating the settings after the parsing is completed.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :param remaining_argv: the remaining argv after the parsing is completed.
        :return: a list of error messages or an empty list
        """
        errors: list[str] = []
        # we want the default for the get command to get both project.version and tool.poetry.version.
        # if a single argument is given (i.e., --project or --poetry), then we want to just get that version.
        if settings.command == "get" and (not settings.project and not settings.poetry):
            settings.project = True
            settings.poetry = True

        return errors


def main(args: list[str] | None = None) -> int:
    """The command line applications main function."""
    with Settings(args=args) as settings:
        # some info commands (--version, --longhelp) need to exit immediately
        # after completion.  The quick_exit flag indicates if this is the case.
        if settings.quick_exit:
            return 0

        commands = {
            "set": set_command,
            "get": get_command,
            "bump": bump_command,
            "release": release_command,
            "version": version_command,
        }

        try:
            commands[settings.command](settings)
        except ValueError as ex:
            logger.error(ex)
            return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(args=None))
