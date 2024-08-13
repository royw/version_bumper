# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture
from loguru import logger

from version_bumper.commands import bump_command, release_command, set_command


def test_bump_version_no_versions() -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write("[project]\n[tool.poetry]\n")
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        with pytest.raises(ValueError, match="Unable to extract neither project.version nor tool.poetry.version"):
            bump_command(settings)


def test_bump_version_different_versions() -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write('[project]\nversion = "1.2.3"\n[tool.poetry]\nversion = "2.3.4"\n')
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        with pytest.raises(ValueError, match="project.version 1.2.3 does not match tool.poetry.version 2.3.4"):
            bump_command(settings)


def test_bump_version_no_project_version() -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write('[project]\n[tool.poetry]\nversion = "1.2.3"\n')
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        with pytest.raises(ValueError, match="project.version None does not match tool.poetry.version"):
            bump_command(settings)


def test_bump_version_no_poetry_version(capsys: CaptureFixture[Any]) -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write('[project]\nversion = "1.2.3"\n[tool.poetry]\n')
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        settings.json = False
        settings.text = False
        bump_command(settings)
        captured = capsys.readouterr()
        assert "1.3.0" in captured.err


def test_release_version_no_versions() -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write("[project]\n[tool.poetry]\n")
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        with pytest.raises(ValueError, match="Unable to extract neither project.version nor tool.poetry.version"):
            release_command(settings)


def test_set_version_part_no_versions() -> None:
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test_pyproject.toml"
        with filepath.open("w") as f:
            f.write("[project]\n[tool.poetry]\n")
        settings = argparse.Namespace()
        settings.pyproject_toml_path = filepath
        settings.part = "minor"
        with pytest.raises(ValueError, match="Unable to extract neither project.version nor tool.poetry.version"):
            set_command(settings)
