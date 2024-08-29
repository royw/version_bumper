# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from importlib.metadata import version
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from version_bumper.__main__ import main

tests_dir = Path(__file__).parent
tmp_dir = tests_dir / "tmp"
tmp_dir.mkdir(exist_ok=True)
good_pyproject_toml_path = tests_dir / "good_pyproject.toml"
non_existing_pyproject_toml_path = tests_dir / "non-existing-file-pyproject.toml"

STARTING_VERSION_STR = "0.1.1a2.post1.dev2+foo0123"


@contextmanager
def unique_pyproject_toml(version_str: str = STARTING_VERSION_STR) -> Generator[str, None, None]:
    """
    A context manager for creating a temporary copy of "good_pyproject.toml" and giving it
    a known starting version.  This allows a test to do whatever they want with the file as
    it will be deleted at the end of the context.
    """
    with tempfile.NamedTemporaryFile("wt", dir=tmp_dir, prefix="pyproject-", suffix=".toml", delete=True) as tf:
        shutil.copy(src=good_pyproject_toml_path, dst=tf.name)
        main(["version", version_str, "--pyproject", tf.name])
        yield tf.name


# app options


def test_main_version(capsys: CaptureFixture[Any]) -> None:
    assert main(["--version"]) == 0
    captured = capsys.readouterr()
    assert version("version_bumper") in captured.out


def test_main_longhelp() -> None:
    assert main(["--longhelp"]) == 0


def test_main_help(capsys: CaptureFixture[Any]) -> None:
    # --help is handled from argparse
    # this testing pattern from: https://dev.to/boris/testing-exit-codes-with-pytest-1g27
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.type is SystemExit
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "--version" in captured.out


def test_invalid_loglevel(capsys: CaptureFixture[Any]) -> None:
    with pytest.raises(SystemExit):
        main(["--loglevel", "1"])
    captured = capsys.readouterr()
    assert "error: argument --loglevel:" in captured.err


def test_logfile() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_logfile.log"
        assert main(["--longhelp", "--logfile", str(filepath)]) == 0
        assert filepath.exists()
        assert filepath.is_file()
        assert filepath.stat().st_size > 0


# command: get


def test_get_json_both(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--json", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        x = json.loads(captured.out)
        y = {"project.version": STARTING_VERSION_STR, "tool.poetry.version": STARTING_VERSION_STR}
        shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
        assert len(shared_items) == 2


def test_get_json_project(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--json", "--project", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        x = json.loads(captured.out)
        y = {"project.version": STARTING_VERSION_STR}
        shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
        assert len(shared_items) == 1


def test_get_json_poetry(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--json", "--poetry", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        x = json.loads(captured.out)
        y = {"tool.poetry.version": STARTING_VERSION_STR}
        shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
        assert len(shared_items) == 1


def test_get_text_both(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--text", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"{STARTING_VERSION_STR}\n{STARTING_VERSION_STR}\n"


def test_get_text_project(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--text", "--project", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"{STARTING_VERSION_STR}\n"


def test_get_text_poetry(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--text", "--poetry", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"{STARTING_VERSION_STR}\n"


def test_get_both(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert (
            captured.out == f"project.version: {STARTING_VERSION_STR}\ntool.poetry.version: {STARTING_VERSION_STR}\n"
        )


def test_get_project(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--project", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"project.version: {STARTING_VERSION_STR}\n"


def test_get_poetry(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["get", "--poetry", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"tool.poetry.version: {STARTING_VERSION_STR}\n"


# command: bump


def test_bump_epoch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "epoch", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"version: 1!{STARTING_VERSION_STR}\n"
        assert main(["bump", "epoch", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == f"version: 2!{STARTING_VERSION_STR}\n"


def test_bump_major(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "major", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 1.0.0\n"
        assert main(["bump", "major", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2.0.0\n"


# def test_bump_minor(capsys: CaptureFixture[Any]) -> None:
def test_bump_minor(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "minor", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.2.0\n"
        assert main(["bump", "minor", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.3.0\n"


# def test_bump_patch(capsys: CaptureFixture[Any]) -> None:
def test_bump_patch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "patch", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.2\n"
        assert main(["bump", "patch", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.3\n"


def test_bump_a(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "a", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a3\n"
        assert main(["bump", "a", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a4\n"


def test_bump_b(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "b", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1b1\n"
        assert main(["bump", "b", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1b2\n"


def test_bump_rc(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "rc", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1rc1\n"
        assert main(["bump", "rc", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1rc2\n"


def test_bump_post(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "post", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post2\n"
        assert main(["bump", "post", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post3\n"


def test_bump_dev(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "dev", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev3\n"
        assert main(["bump", "dev", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev4\n"


def test_bump_local(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["bump", "local", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev2+foo0124\n"
        assert main(["bump", "local", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev2+foo0125\n"


# command: set


def test_set_epoch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "epoch", "2", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2!0.1.1a2.post1.dev2+foo0123\n"


def test_set_major(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "major", "2", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2.1.1a2.post1.dev2+foo0123\n"


def test_set_minor(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "minor", "2", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.2.1a2.post1.dev2+foo0123\n"


def test_set_patch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "patch", "2", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.2a2.post1.dev2+foo0123\n"


def test_set_a(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "a", "4", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a4.post1.dev2+foo0123\n"


def test_set_b(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "b", "4", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1b4.post1.dev2+foo0123\n"


def test_set_rc(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "rc", "4", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1rc4.post1.dev2+foo0123\n"


def test_set_post(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "post", "4", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post4.dev2+foo0123\n"


def test_set_dev(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "dev", "4", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev4+foo0123\n"


def test_set_local(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "local", "ubuntu-1", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev2+ubuntu.1\n"


def test_set_clear_right_epoch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "epoch", "2", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2!0.0.0\n"


def test_set_clear_right_major(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "major", "2", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2.0.0\n"


def test_set_clear_right_minor(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "minor", "2", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.2.0\n"


def test_set_clear_right_patch(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "patch", "2", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.2\n"


def test_set_clear_right_a(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "a", "4", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a4\n"


def test_set_clear_right_b(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "b", "4", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1b4\n"


def test_set_clear_right_rc(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "rc", "4", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1rc4\n"


def test_set_clear_right_post(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "post", "4", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post4\n"


def test_set_clear_right_dev(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "dev", "4", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev4\n"


def test_set_clear_right_local(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["set", "local", "ubuntu-1", "--clear-right", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1a2.post1.dev2+ubuntu.1\n"


# command: version


def test_version(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["version", "2!1.2rc3", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 2!1.2rc3\n"
        capsys.readouterr()  # clear captured output
        assert main(["get", "--project", "--text", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "2!1.2rc3\n"
        capsys.readouterr()  # clear captured output
        assert main(["get", "--poetry", "--text", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "2!1.2rc3\n"


def test_invalid_version(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["version", "1.2.3.", "--pyproject", pyproject_filename]) == 1
        captured = capsys.readouterr()
        assert captured.out == "Invalid version string: 1.2.3.\n"


# command: release


def test_release(capsys: CaptureFixture[Any]) -> None:
    with unique_pyproject_toml(version_str=STARTING_VERSION_STR) as pyproject_filename:
        capsys.readouterr()  # clear captured output from setting version in unique_pyproject_toml
        assert main(["release", "--pyproject", pyproject_filename]) == 0
        captured = capsys.readouterr()
        assert captured.out == "version: 0.1.1\n"


def test_get_file_not_found(capsys: CaptureFixture[Any]) -> None:
    assert main(["get", "--pyproject", str(non_existing_pyproject_toml_path)]) == 1
    captured = capsys.readouterr()
    assert "File not found" in captured.out


def test_set_file_not_found(capsys: CaptureFixture[Any]) -> None:
    assert main(["set", "local", "test", "--pyproject", str(non_existing_pyproject_toml_path)]) == 1
    captured = capsys.readouterr()
    assert "File not found" in captured.out


def test_no_arguments(capsys: CaptureFixture[Any]) -> None:
    """argparse.parse_known_args calls sys.exit() when missing arguments"""
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.type is SystemExit
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "Version Bumper: error:" in captured.err


def test_set_no_arguments(capsys: CaptureFixture[Any]) -> None:
    """argparse.parse_known_args calls sys.exit() when missing arguments"""
    with pytest.raises(SystemExit) as e:
        main(["set"])
    assert e.type is SystemExit
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "Version Bumper set: error:" in captured.err


def test_version_no_arguments(capsys: CaptureFixture[Any]) -> None:
    assert main(["version", "--pyproject", str(non_existing_pyproject_toml_path)]) == 1
    captured = capsys.readouterr()
    assert "Invalid version string" in captured.out


def test_unsupported_arguments(capsys: CaptureFixture[Any]) -> None:
    with pytest.raises(SystemExit) as e:
        main(["--foobar"])
    assert e.type is SystemExit
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "Version Bumper: error: The following arguments are unrecognized/unsupported: ['--foobar']" in captured.err
