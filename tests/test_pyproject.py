# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from version_bumper.pyproject import PyProject
from version_bumper.version import Version

tests_dir = Path(__file__).parent


def test_load_invalid_key() -> None:
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    missing_version = PyProject.load_version(pyproject_toml_path=good_pyproject_path, key_dot_notation="xyzzy.version")
    assert missing_version is None


def test_load_version() -> None:
    # copy good_pyproject.toml to a temporary location so we can
    # modify it.
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    project_version = PyProject.load_version(
        pyproject_toml_path=good_pyproject_path, key_dot_notation="project.version"
    )
    poetry_version = PyProject.load_version(
        pyproject_toml_path=good_pyproject_path, key_dot_notation="tool.poetry.version"
    )
    assert project_version is not None
    assert (
        poetry_version == project_version
    ), f"project.version:{project_version} != tool.poetry.version:{poetry_version}"


def test_save_version() -> None:
    # copy good_pyproject.toml to a temporary directory as test_pyproject.toml.
    good_pyproject_path = tests_dir / "good_pyproject.toml"
    with tempfile.TemporaryDirectory() as tmp:
        pyproject_toml_path = Path(tmp) / "test_pyproject.toml"
        pyproject_toml_path.unlink(missing_ok=True)
        assert good_pyproject_path.exists()
        shutil.copy2(str(good_pyproject_path), str(pyproject_toml_path))

        # get project.version and tool.poetry.version from the test_pyproject.toml
        project_version = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation="project.version"
        )
        poetry_version = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation="tool.poetry.version"
        )

        # make sure they are not our test version
        assert str(project_version) != "1.2.3.dev1"
        assert poetry_version != Version("1.2.3.dev1")

        # update the test_pyproject.toml with our test version for both project.version and tool.poetry.version
        PyProject.save_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation="project.version", version=Version("1.2.3.dev1")
        )

        PyProject.save_version(
            pyproject_toml_path=pyproject_toml_path,
            key_dot_notation="tool.poetry.version",
            version=Version("1.2.3.dev1"),
        )

        # now make sure the file has our test version for both project.version and tool.poetry.version
        project_version = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation="project.version"
        )
        poetry_version = PyProject.load_version(
            pyproject_toml_path=pyproject_toml_path, key_dot_notation="tool.poetry.version"
        )

        assert str(project_version) == "1.2.3.dev1"
        assert poetry_version == Version("1.2.3.dev1")
