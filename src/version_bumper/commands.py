# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path

from loguru import logger

from version_bumper.pyproject import PyProject
from version_bumper.version import Version


def version_command(settings: argparse.Namespace) -> None:
    """
    Set the version in the pyproject.toml file.
    """
    __save_version(pyproject_toml_path=settings.pyproject_toml_path, version=Version(settings.value))
    if not settings.silent:
        __output(settings=settings, versions={"version": str(settings.value)})


def get_command(settings: argparse.Namespace) -> None:
    """
    Get the version (project.version, or tool.poetry.version, or both) from the pyproject.toml file.
    """
    versions: dict[str, str] = {}
    keys: list[str] = []

    keys.append("project.version") if settings.project else None
    keys.append("tool.poetry.version") if settings.poetry else None

    version_list: list[Version | None] = PyProject.load_version(
        pyproject_toml_path=settings.pyproject_toml_path, key_dot_notation_list=keys
    )
    if settings.project and version_list is not None:
        versions["project.version"] = str(version_list.pop(0))

    if settings.poetry and version_list is not None:
        versions["tool.poetry.version"] = str(version_list.pop(0))
    __output(settings=settings, versions=versions)


def bump_command(settings: argparse.Namespace) -> None:
    """
    A version consists of several parts: epoch, major, minor, patch, release, a, b, rc, post, dev, and local.
    This method allows incrementing any of the individual parts.
    """
    version: Version | None = __load_version(settings=settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.bump(part=settings.part)
    __save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    __output(settings=settings, versions={"version": str(version)})


def release_command(settings: argparse.Namespace) -> None:
    """
    A release version consists of several parts: epoch, major, minor, and patch.
    This method removes the remaining parts: a, b, rc, post, dev, and local.
    """
    version: Version | None = __load_version(settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.bump_release()
    __save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    __output(settings=settings, versions={"version": str(version)})


def set_command(settings: argparse.Namespace) -> None:
    """
    A version consists of several parts: epoch, major, minor, patch, release, a, b, rc, post, dev, and local.
    This method allows setting any of the individual parts.
    """
    version: Version | None = __load_version(settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.set(part=settings.part, value=settings.value, clear_right=settings.clear_right)
    __save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    __output(settings=settings, versions={"version": str(version)})


def __save_version(pyproject_toml_path: Path, version: Version) -> None:
    """
    Saves the version to the pyproject.toml file.  Always overwrites the project.version.
    If the pyproject.toml file already has a tool.poetry.version, it will be overwritten,
    but will not be created.
    """
    # if tool.poetry.version exists, then overwrite it
    versions: list[Version | None] = PyProject.load_version(
        pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=["tool.poetry.version"]
    )

    keys = ["project.version"]
    if versions[0] is not None:
        # only update tool.poetry.version, i.e. DO NOT CREATE
        keys.append("tool.poetry.version")

    # always save to project.version
    PyProject.save_version(pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=keys, version=version)


def __sanity_check_loaded_versions(project_version: Version | None, poetry_version: Version | None) -> Version | None:
    """
    A pyproject.toml file must contain project.version and optionally tool.poetry.version.
    This method returns the project version and will raise ValueError if tool.poetry.version exists and doesn't
    match the project.version.
    """
    if poetry_version is not None and project_version != poetry_version:
        errmsg = f"project.version {project_version!s} does not match tool.poetry.version {poetry_version!s}"
        raise ValueError(errmsg)
    return project_version


def __load_version(settings: argparse.Namespace) -> Version | None:
    """
    Loads the version from the pyproject.toml file.
    """
    # try to load both project.version and tool.poetry.version
    versions: list[Version | None] = PyProject.load_version(
        pyproject_toml_path=settings.pyproject_toml_path,
        key_dot_notation_list=["project.version", "tool.poetry.version"],
    )
    # sanity check what we loaded
    return __sanity_check_loaded_versions(versions[0], versions[1])


def __output(settings: argparse.Namespace, versions: dict[str, str]) -> None:
    """
    Formats and outputs the version(s) to the logger.  The supported formats are:
    --json, --text, and default, where default is human-readable meant for the console.
    """
    if settings.json:
        logger.info(json.dumps(versions))
    elif settings.text:
        logger.info("\n".join([str(versions[key]) for key in versions]))
    else:
        for key, value in versions.items():
            logger.info(f"{key}: {value}")
