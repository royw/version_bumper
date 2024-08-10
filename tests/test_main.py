# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from version_bumper.__main__ import main

tests_dir = Path(__file__).parent


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


def test_get_version(capsys: CaptureFixture[Any]) -> None:
    assert main(["get"]) == 0
    captured = capsys.readouterr()
    assert "project.version" in captured.err
    assert "tool.poetry.version" in captured.err


def test_get_project_version(capsys: CaptureFixture[Any]) -> None:
    assert main(["get", "--project"]) == 0
    captured = capsys.readouterr()
    assert "project.version" in captured.err
    assert "tool.poetry.version" not in captured.err


def test_get_poetry_version(capsys: CaptureFixture[Any]) -> None:
    assert main(["get", "--poetry"]) == 0
    captured = capsys.readouterr()
    assert "project.version" not in captured.err
    assert "tool.poetry.version" in captured.err


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
