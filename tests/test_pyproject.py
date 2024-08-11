# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from version_bumper.pyproject import PyProject
from version_bumper.version import Version

tests_dir = Path(__file__).parent


def test_load_invalid_key() -> None:
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    with pytest.raises(AttributeError):
        PyProject.load_version(pyproject_toml_path=good_pyproject_path, key_dot_notation_list=["xyzzy.version"])


def test_load_version() -> None:
    # copy good_pyproject.toml to a temporary location so we can
    # modify it.
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    versions = PyProject.load_version(
        pyproject_toml_path=good_pyproject_path, key_dot_notation_list=["project.version", "tool.poetry.version"]
    )
    assert versions[0] is not None
    assert versions[1] == versions[0], f"project.version:{versions[0]} != tool.poetry.version:{versions[1]}"


def test_save_version() -> None:
    # copy good_pyproject.toml to a temporary directory as test_pyproject.toml.
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    with tempfile.TemporaryDirectory() as tmp:
        pyproject_toml_path = Path(tmp) / "test_pyproject.toml"
        pyproject_toml_path.unlink(missing_ok=True)
        assert good_pyproject_path.exists()
        shutil.copy2(str(good_pyproject_path), str(pyproject_toml_path))

        # get project.version and tool.poetry.version from the test_pyproject.toml
        versions = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=["project.version", "tool.poetry.version"]
        )

        # make sure they are not our test version
        assert str(versions[0]) != "1.2.3.dev1"
        assert versions[1] != Version("1.2.3.dev1")

        # update the test_pyproject.toml with our test version for both project.version and tool.poetry.version
        PyProject.save_version(
            pyproject_toml_path=pyproject_toml_path,
            key_dot_notation_list=["project.version", "tool.poetry.version"],
            version=Version("1.2.3.dev1"),
        )

        # now make sure the file has our test version for both project.version and tool.poetry.version
        versions = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=["project.version", "tool.poetry.version"]
        )

        assert str(versions[0]) == "1.2.3.dev1"
        assert versions[1] == Version("1.2.3.dev1")
