# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from importlib.metadata import version
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from version_bumper.__main__ import main

tests_dir = Path(__file__).parent
good_pyproject_toml_path = tests_dir / "good_pyproject.toml"


@pytest.fixture()
def starting_version() -> Generator[str, None, str]:
    version_str = "0.1.1a0"
    try:
        assert main(["version", version_str, "--pyproject", str(good_pyproject_toml_path)]) == 0
        yield version_str
    finally:
        assert main(["version", version_str, "--pyproject", str(good_pyproject_toml_path)]) == 0

    return version_str


# app options


def test_main_version(capsys: CaptureFixture[Any]) -> None:
    assert main(["--version"]) == 0
    captured = capsys.readouterr()
    assert version("version_bumper") in captured.err


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


def test_get_json_both(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--json", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    x = json.loads(captured.err)
    y = {"project.version": starting_version, "tool.poetry.version": starting_version}
    shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
    assert len(shared_items) == 2


def test_get_json_project(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--json", "--project", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    x = json.loads(captured.err)
    y = {"project.version": starting_version}
    shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
    assert len(shared_items) == 1


def test_get_json_poetry(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--json", "--poetry", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    x = json.loads(captured.err)
    y = {"tool.poetry.version": starting_version}
    shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
    assert len(shared_items) == 1


def test_get_text_both(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--text", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"{starting_version}\n{starting_version}\n"


def test_get_text_project(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--text", "--project", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"{starting_version}\n"


def test_get_text_poetry(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--text", "--poetry", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"{starting_version}\n"


def test_get_both(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"project.version: {starting_version}\ntool.poetry.version: {starting_version}\n"


def test_get_project(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--project", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"project.version: {starting_version}\n"


def test_get_poetry(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["get", "--poetry", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"tool.poetry.version: {starting_version}\n"


# command: bump


def test_bump_epoch(capsys: CaptureFixture[Any], starting_version: str) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "epoch", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"version: 1!{starting_version}\n"
    assert main(["bump", "epoch", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"version: 2!{starting_version}\n"


def test_bump_major(capsys: CaptureFixture[Any]) -> None:
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "major", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 1.0.0\n"
    assert main(["bump", "major", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2.0.0\n"


# def test_bump_minor(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_patch(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_a(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_b(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_rc(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_post(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_dev(capsys: CaptureFixture[Any]) -> None:
#
# def test_bump_local(capsys: CaptureFixture[Any]) -> None:


# command: set

# command: version

# command: release
