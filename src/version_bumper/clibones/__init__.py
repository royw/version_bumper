# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

"""
# CLI Bones

This application used [cookiecutter-clibones](https://github.com/royw/cookiecutter-clibones), a CLI application
framework based on the argparse standard library with loguru logging.
[Poetry](https://python-poetry.org/) and [Task](https://taskfile.dev/) are used for project
management.

## Architecture

The architecture used is a Settings context manager that handles all the command line and config file argument
definition, parsing, and validation.

The application's entry point is in `version_bumper/__main__.py`
In `__main.py__` there several TODOs that you will need to visit and clear.

The application may be run with any of the following:

  * `python3 -m clibones --help`
  * `poetry run python3 -m clibones --help`
  * `task main --help`

So in general, for each command line argument you ought to:

* optionally add an argument group to the parser in `Settings.add_arguments()`
* add argument to the parser in `Settings.add_arguments()`
* optionally add validation to `Settings.validate_arguments()`

Refer to `application_settings.py` which implements help and logging as examples.

The `__example_application()` demonstrates using a `GracefulInterruptHandler` to capture ^C for a main loop.

Next take a look at `main.main()` which demonstrates the use of the Settings context manager.

The `Settings` does have a few extra features including:

* config files are supported for any command arguments you want to persist.
* standard logging setup via command line arguments.

"""
