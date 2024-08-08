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

import atexit
import sys
from collections.abc import Sequence
from pprint import pformat
from time import sleep
from typing import TYPE_CHECKING

from loguru import logger

from version_bumper.clibones.application_settings import ApplicationSettings
from version_bumper.clibones.graceful_interrupt_handler import GracefulInterruptHandler

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence

DEFAULT_COUNT = 5
MAX_COUNT = 10
MIN_COUNT = 0


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

    # TODO: verify the __project_* variables are correct

    __project_name: str = "version_bumper"
    """The name of the project"""

    __project_package: str = "version_bumper"
    """The name of the package this settings belongs to. """

    __project_description: str = (
        "Python package version utility to bump a version by parts."
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
        self.add_persist_keys({"pyproject_toml_files", "loglevel", "debug"})

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

        # TODO: Remove example app --count N argument
        app_group = parser.add_argument_group("Application arguments")
        app_group.add_argument(
            "--count",
            type=int,
            default=DEFAULT_COUNT,
            help=f"How many times (0-{MAX_COUNT} to execute the example loop (default: {DEFAULT_COUNT})",
        )

    def validate_arguments(self, settings: argparse.Namespace, remaining_argv: list[str]) -> list[str]:  # noqa: ARG002
        """This provides a hook for validating the settings after the parsing is completed.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :param remaining_argv: the remaining argv after the parsing is completed.
        :return: a list of error messages or an empty list
        """
        result = []
        # TODO: Remove example app validation: --count=N where: MIN_COUNT < N <= MAX_COUNT
        if settings.count > MAX_COUNT:
            result.append(f"--count ({settings.count}) > 10")
        if settings.count < MIN_COUNT:
            result.append(f"--count ({settings.count}) < {MIN_COUNT}")
        return result


# TODO: remove example application
def __example_application(settings: argparse.Namespace) -> None:
    """This is just an example application, replace with the real application.

    :param settings: the settings object returned by ArgumentParser.parse_args()
    """
    with GracefulInterruptHandler() as handler:
        logger.debug("Executing Example Application")
        logger.info(f"Settings: {pformat(vars(settings), indent=2)}")

        for iteration in range(settings.count):
            sleep(1)
            logger.info(".", end="", flush=True)
            # to break out of loop when interrupt (^C) is pressed
            if handler.interrupted:
                logger.error(f"Loop Interrupted after {iteration} iterations")
                break
        logger.info("\n")

        logger.debug("Example Application Complete")


def main(args: list[str] | None = None) -> int:
    """The command line applications main function."""
    with Settings(args=args) as settings:
        # some info commands (--version, --longhelp) need to exit immediately
        # after completion.  The quick_exit flag indicates if this is the case.
        if settings.quick_exit:
            return 0
        # TODO: replace invoking the example application with your application's entry point
        __example_application(settings)
    return 0


def cleanup() -> None:  # pragma: no cover
    """Cleans up the application just before exiting."""
    # TODO: add any cleanup necessary.
    logger.debug("Cleaning up")


if __name__ == "__main__":  # pragma: no cover
    atexit.register(cleanup)
    sys.exit(main(args=None))
