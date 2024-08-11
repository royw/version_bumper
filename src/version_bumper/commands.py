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
    save_version(pyproject_toml_path=settings.pyproject_toml_path, version=Version(settings.value))
    if not settings.silent:
        output(settings, {"version": str(settings.value)})


def get_command(settings: argparse.Namespace) -> None:
    versions: dict[str, str] = {}
    keys: list[str] = []

    keys.append("project.version") if settings.project else None
    keys.append("tool.poetry.version") if settings.poetry else None

    version_list: list[Version] = PyProject.load_version(
        pyproject_toml_path=settings.pyproject_toml_path, key_dot_notation_list=keys
    )
    if settings.project:
        versions["project.version"] = str(version_list.pop(0))

    if settings.poetry:
        versions["tool.poetry.version"] = str(version_list.pop(0))
    output(settings, versions)


def __sanity_check_loaded_versions(project_version: Version | None, poetry_version: Version | None) -> Version | None:
    version = None
    if project_version and poetry_version:
        if project_version != poetry_version:
            errmsg = f"project.version {project_version!s} does not match tool.poetry.version {poetry_version!s}"
            raise ValueError(errmsg)
        version = project_version
    elif project_version:
        version = project_version
    elif poetry_version:
        version = poetry_version
    return version


def save_version(pyproject_toml_path: Path, version: Version) -> None:
    # if tool.poetry.version exists, then overwrite it
    versions: list[Version] = PyProject.load_version(
        pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=["tool.poetry.version"]
    )

    keys = ["project.version"]
    if versions:
        # only update tool.poetry.version, i.e. DO NOT CREATE
        keys.append("tool.poetry.version")

    # always save to project.version
    PyProject.save_version(pyproject_toml_path=pyproject_toml_path, key_dot_notation_list=keys, version=version)


def __load_version(settings: argparse.Namespace) -> Version | None:
    # try to load both project.version and tool.poetry.version
    versions: list[Version] = PyProject.load_version(
        pyproject_toml_path=settings.pyproject_toml_path,
        key_dot_notation_list=["project.version", "tool.poetry.version"],
    )
    # sanity check what we loaded
    return __sanity_check_loaded_versions(versions[0], versions[1])


def bump_command(settings: argparse.Namespace) -> None:
    version: Version | None = __load_version(settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.bump(settings.part)
    save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    output(settings, {"version": str(version)})


def release_command(settings: argparse.Namespace) -> None:
    version: Version | None = __load_version(settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.bump_release()
    save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    output(settings, {"version": str(version)})


def set_command(settings: argparse.Namespace) -> None:
    version: Version | None = __load_version(settings)
    if version is None:
        errmsg = (
            f"Unable to extract neither project.version nor tool.poetry.version "
            f" from {settings.pyproject_toml_path}"
        )
        raise ValueError(errmsg)

    version.set(part=settings.part, value=settings.value)
    save_version(pyproject_toml_path=settings.pyproject_toml_path, version=version)
    output(settings, {"version": str(version)})


def output(settings: argparse.Namespace, versions: dict[str, str]) -> None:
    if settings.json:
        logger.info(json.dumps(versions))
    elif settings.text:
        logger.info("\n".join([str(versions[key]) for key in versions]))
    else:
        for key, value in versions.items():
            logger.info(f"{key}: {value}")
