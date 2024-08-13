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
    version_str = "0.1.1a2.post1.dev2+foo0123"
    try:
        assert main(["version", version_str, "--silent", "--pyproject", str(good_pyproject_toml_path)]) == 0
        yield version_str
    finally:
        assert main(["version", version_str, "--silent", "--pyproject", str(good_pyproject_toml_path)]) == 0

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


def test_bump_major(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "major", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 1.0.0\n"
    assert main(["bump", "major", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2.0.0\n"


# def test_bump_minor(capsys: CaptureFixture[Any]) -> None:
def test_bump_minor(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "minor", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.2.0\n"
    assert main(["bump", "minor", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.3.0\n"


# def test_bump_patch(capsys: CaptureFixture[Any]) -> None:
def test_bump_patch(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "patch", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.2\n"
    assert main(["bump", "patch", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.3\n"


def test_bump_a(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "a", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a3\n"
    assert main(["bump", "a", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a4\n"


def test_bump_b(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "b", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1b1\n"
    assert main(["bump", "b", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1b2\n"


def test_bump_rc(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "rc", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1rc1\n"
    assert main(["bump", "rc", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1rc2\n"


def test_bump_post(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "post", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post2\n"
    assert main(["bump", "post", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post3\n"


def test_bump_dev(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "dev", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev3\n"
    assert main(["bump", "dev", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev4\n"


def test_bump_local(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["bump", "local", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev2+foo0124\n"
    assert main(["bump", "local", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev2+foo0125\n"


# command: set


def test_set_epoch(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "epoch", "2", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2!0.1.1a2.post1.dev2+foo0123\n"


def test_set_major(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "major", "2", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2.1.1a2.post1.dev2+foo0123\n"


def test_set_minor(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "minor", "2", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.2.1a2.post1.dev2+foo0123\n"


def test_set_patch(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "patch", "2", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.2a2.post1.dev2+foo0123\n"


def test_set_a(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "a", "4", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a4.post1.dev2+foo0123\n"


def test_set_b(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "b", "4", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1b4.post1.dev2+foo0123\n"


def test_set_rc(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "rc", "4", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1rc4.post1.dev2+foo0123\n"


def test_set_post(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "post", "4", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post4.dev2+foo0123\n"


def test_set_dev(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "dev", "4", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev4+foo0123\n"


def test_set_local(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "local", "ubuntu-1", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev2+ubuntu.1\n"


def test_set_clear_right_epoch(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "epoch", "2", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2!0.0.0\n"


def test_set_clear_right_major(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "major", "2", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2.0.0\n"


def test_set_clear_right_minor(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "minor", "2", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.2.0\n"


def test_set_clear_right_patch(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "patch", "2", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.2\n"


def test_set_clear_right_a(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "a", "4", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a4\n"


def test_set_clear_right_b(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "b", "4", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1b4\n"


def test_set_clear_right_rc(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "rc", "4", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1rc4\n"


def test_set_clear_right_post(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "post", "4", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post4\n"


def test_set_clear_right_dev(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "dev", "4", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev4\n"


def test_set_clear_right_local(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["set", "local", "ubuntu-1", "--clear-right", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1a2.post1.dev2+ubuntu.1\n"


# command: version


def test_version(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["version", "2!1.2rc3", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 2!1.2rc3\n"
    capsys.readouterr()  # clear captured output
    assert main(["get", "--project", "--text", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "2!1.2rc3\n"
    capsys.readouterr()  # clear captured output
    assert main(["get", "--poetry", "--text", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "2!1.2rc3\n"


def test_invalid_version(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["version", "1.2.3.", "--pyproject", str(good_pyproject_toml_path)]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Invalid version string: 1.2.3.\n"


# command: release


def test_release(capsys: CaptureFixture[Any], starting_version: str) -> None:  # noqa: ARG001
    capsys.readouterr()  # clear captured output from starting_version fixture
    assert main(["release", "--pyproject", str(good_pyproject_toml_path)]) == 0
    captured = capsys.readouterr()
    assert captured.err == "version: 0.1.1\n"
