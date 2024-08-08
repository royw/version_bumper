# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any

import pytest
import tomlkit
from _pytest.capture import CaptureFixture

from version_bumper.__main__ import main

tests_dir = Path(__file__).parent


def test_main_pyproject() -> None:
    assert main(["--count", "0"]) == 0


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


def test_quiet(capsys: CaptureFixture[Any]) -> None:
    assert main(["--count", "0", "--quiet", "--config", str(tests_dir / "config_2.toml")]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""


def test_invalid_loglevel(capsys: CaptureFixture[Any]) -> None:
    with pytest.raises(SystemExit):
        main(["--count", "0", "--loglevel", "1", "--config", str(tests_dir / "config_2.toml")])
    captured = capsys.readouterr()
    assert "error: argument --loglevel:" in captured.err


def test_logfile() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_logfile.log"
        assert main(["--longhelp", "--logfile", str(filepath)]) == 0
        assert filepath.exists()
        assert filepath.is_file()
        assert filepath.stat().st_size > 0


def test_load_config_file_debug(capsys: CaptureFixture[Any]) -> None:
    # with debug=true
    assert main(["--count", "0", "--config", str(tests_dir / "config_1.toml")]) == 0
    captured = capsys.readouterr()
    assert "'debug': True" in captured.err


def test_load_config_file_not_debug(capsys: CaptureFixture[Any]) -> None:
    # with debug=false
    assert main(["--count", "0", "--config", str(tests_dir / "config_2.toml")]) == 0
    captured = capsys.readouterr()
    assert "'debug': False" in captured.err


def test_load_config_file_loglevel_debug(capsys: CaptureFixture[Any]) -> None:
    # with loglevel=DEBUG
    assert main(["--count", "0", "--config", str(tests_dir / "config_3.toml")]) == 0
    captured = capsys.readouterr()
    assert "'loglevel': 'DEBUG'" in captured.err


def test_load_config_file_loglevel_info(capsys: CaptureFixture[Any]) -> None:
    # with loglevel=INFO
    assert main(["--count", "0", "--config", str(tests_dir / "config_4.toml")]) == 0
    captured = capsys.readouterr()
    assert "'loglevel': 'INFO'" in captured.err


def test_debug_flags(capsys: CaptureFixture[Any]) -> None:
    # with debug=true
    assert main(["--count", "0", "--debug"]) == 0
    captured = capsys.readouterr()
    assert "'debug': True" in captured.err


def test_debug_flags_false(capsys: CaptureFixture[Any]) -> None:
    # with debug=false
    assert (
        main(
            [
                "--count",
                "0",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "'debug': False" in captured.err


def test_debug_flags_debug(capsys: CaptureFixture[Any]) -> None:
    # with --loglevel DEBUG
    assert main(["--count", "0", "--loglevel", "DEBUG"]) == 0
    captured = capsys.readouterr()
    assert "'loglevel': 'DEBUG'" in captured.err


def test_debug_flags_info(capsys: CaptureFixture[Any]) -> None:
    # with --loglevel INFO
    assert main(["--count", "0", "--loglevel", "INFO"]) == 0
    captured = capsys.readouterr()
    assert "'loglevel': 'INFO'" in captured.err


def test_save_config_file_as() -> None:
    test_save_config_filepath = tests_dir / "config_save_1.toml"

    test_save_config_filepath.unlink(missing_ok=True)

    assert (
        main(
            [
                "--count",
                "0",
                "--loglevel",
                "DEBUG",
                "--save-config-as",
                str(test_save_config_filepath),
                str(tests_dir / "good_pyproject.toml"),
            ]
        )
        == 0
    )

    assert test_save_config_filepath.exists()
    with test_save_config_filepath.open() as fp:
        data: dict[str, Any] = tomlkit.load(fp).value
        assert "loglevel" in data["version_bumper"]
        assert data["version_bumper"]["loglevel"] == "DEBUG"

    test_save_config_filepath.unlink(missing_ok=True)


def test_save_config_file() -> None:
    """
    Test loading a config file, then saving a changed version of it.
    """
    # Copy config_3.toml to config_save_2.toml.
    test_save_config_filepath = tests_dir / "config_save_2.toml"
    test_save_config_filepath.unlink(missing_ok=True)
    test_source_config_file = tests_dir / "config_3.toml"
    assert test_source_config_file.exists()
    shutil.copy2(str(test_source_config_file), str(test_save_config_filepath))

    # Verify loglevel is set to DEBUG in config_save_2.toml.
    with test_save_config_filepath.open() as fp:
        data = tomlkit.load(fp).value
        assert "loglevel" in data["version_bumper"]
        assert data["version_bumper"]["loglevel"] == "DEBUG"

    # Run main using config_save_2.toml as the config file and override
    # the loglevel to be ERROR and save the config file.
    assert (
        main(
            [
                "--count",
                "0",
                "--config",
                str(test_save_config_filepath),
                "--save-config",
                "--loglevel",
                "ERROR",
                str(tests_dir / "good_pyproject.toml"),
            ]
        )
        == 0
    )

    # Verify loglevel is set to ERROR in config_save_2.toml.
    assert test_save_config_filepath.exists()
    with test_save_config_filepath.open() as fp:
        data = tomlkit.load(fp).value
        assert "loglevel" in data["version_bumper"]
        assert data["version_bumper"]["loglevel"] == "ERROR"

    # cleanup
    test_save_config_filepath.unlink(missing_ok=True)
