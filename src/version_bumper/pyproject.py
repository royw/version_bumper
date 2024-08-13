# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit import TOMLDocument

from version_bumper.version import Version


class PyProject:
    @classmethod
    def load_version(cls, pyproject_toml_path: Path, key_dot_notation_list: list[str]) -> list[Version | None]:
        """
        Load the versions specified by a list of dotted keys from the pyproject.toml file.
        """
        versions: list[Version | None] = []
        with pyproject_toml_path.open(encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.load(f)
            for key_dot_notation in key_dot_notation_list:
                field: Any = doc
                for key in key_dot_notation.split("."):
                    field = field.get(key)
                versions.append(Version(field) if field is not None else None)
        return versions

    @classmethod
    def save_version(cls, pyproject_toml_path: Path, key_dot_notation_list: list[str], version: Version) -> None:
        """
        Save the version to each of the dotted keys in the given list to the pyproject.toml file.
        """
        with pyproject_toml_path.open(encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.load(f)
            for key_dot_notation in key_dot_notation_list:
                field: Any = doc
                for key in key_dot_notation.split(".")[:-1]:
                    field = field.get(key)
                field.update({"version": str(version)})

        # write to temporary file then atomically "switch" it with the original using rename.
        with tempfile.NamedTemporaryFile("wt", dir=pyproject_toml_path.parent, delete=False) as tf:
            tf.write(tomlkit.dumps(doc))
            temp_name = Path(tf.name)
        temp_name.rename(pyproject_toml_path)
