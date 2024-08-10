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
    def load_version(cls, pyproject_toml_path: Path, key_dot_notation: str) -> Version | None:
        with pyproject_toml_path.open(encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.load(f)
            field: Any = doc
            try:
                for key in key_dot_notation.split("."):
                    field = field.get(key)
                return Version(field)
            except AttributeError:
                return None

    @classmethod
    def save_version(cls, pyproject_toml_path: Path, key_dot_notation: str, version: Version) -> None:
        with pyproject_toml_path.open(encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.load(f)
            field: Any = doc
            for key in key_dot_notation.split(".")[:-1]:
                field = field.get(key)
            field.update({"version": str(version)})

        # write to temporary file then atomically "switch" it with the original using rename.
        with tempfile.NamedTemporaryFile("wt", dir=pyproject_toml_path.parent, delete=False) as tf:
            tf.write(tomlkit.dumps(doc))
            temp_name = Path(tf.name)
        temp_name.rename(pyproject_toml_path)
