# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

"""
Documentation that will be shown with --longhelp goes here.
Consider using some of your README.md.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

import tomlkit

try:
    # this assumes running in an installed package
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # this should only ever happen in the development environment,
    # so ok to assume location of pyproject.toml file.
    # Also assume src/package file layout and this file is in src/package
    # and pyproject is in the parent directory of src
    # ../../pyproject.toml
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with pyproject_path.open() as fp:
        data = tomlkit.loads(fp.read()).value
        __version__ = data["tool"]["poetry"]["version"] + "dev"
