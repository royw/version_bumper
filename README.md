<!--
SPDX-FileCopyrightText: 2024 Roy Wright

SPDX-License-Identifier: MIT
-->

# Version Bumper

[![PyPI - Version](https://img.shields.io/pypi/v/version_bumper.svg)](https://pypi.org/project/version_bumper)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/version_bumper.svg)](https://pypi.org/project/version_bumper)

---

## Table of Contents

<!-- TOC -->

- [Version Bumper](#version-bumper)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Usage](#usage)
  - [Installation](#installation)
    - [PyPI Installation](#pypi-installation)
    - [Development Installation](#development-installation)
      - [Development Prerequisites](#development-prerequisites)
  - [License](#license)
  - [References](#references)
  <!-- TOC -->

## Overview

Oh, no! Not another version bump utility!

`version_bumper` is a PyPA Version compliant bumper that can bump (increment
by 1) any part of the version and supports pyproject.toml's project.version and
tool.poetry.version key/value pairs.

What this means is:

- `version_bumper` fully complies with the version definition in the Python
  Packaging Authority's (PyPA) (https://www.pypa.io/) Python Packaging User
  Guide
  [Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers)
  specification (originally PEP440).

- `version_bumper` manages the version(s) in the
  [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/#pyproject-toml-spec)
  file.

  - Poetry uses the key/value pair `tool.poetry.version` (expecting this to
    change when version 2 is released)
  - other tools use the current PyPA standard key/value pair `project.version`
  - `project.version` is required to exist.
  - if `tool.poetry.version` exists, then it will be updated when
    `project.version` is updated.
  - if `tool.poetry.version` does not exist, then `version_bumper` will NOT
    create it.

- `version_bumper` lets you set or bump individual parts of the version as well
  as setting or getting the full version.

- `version_bumper` supports input and output in json, text (for bash scripts),
  or human-readable console.

- `version_bumper` has a full suite (100% coverage) of tests that serve as both
  examples and validation.

## Usage

Let's demonstrate what version_bumper can do.

    ➤ version_bumper
    usage: Version Bumper [-h] [--config FILE] [--save-config] [--save-config-as FILE] [-v] [--longhelp] [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--debug] [--quiet] [--logfile LOGFILE]
                          {bump,version,set,get,release} ...
    Version Bumper: error: A command argument (set, get, bump, release, version) or an informational option (--help, --longhelp, --version) is required

OK, so we have to give it a command or an informational option. I'll leave the
informational options as an exercise for the reader.

Valid help commands are:

    ➤ version_bumper --help
    ➤ version_bumper set --help
    ➤ version_bumper get --help
    ...

Let's get the version(s):

    ➤ version_bumper get
    project.version: 0.1.1
    tool.poetry.version: 0.1.1

and as json:

    ➤ version_bumper get --json
    {"project.version": "0.1.1", "tool.poetry.version": "0.1.1"}

and as text:

    ➤ version_bumper get --text
    0.1.1
    0.1.1

For getting the version in a bash script, you probably want to specify which
version and get just a single value:

    ➤ PROJECT_VERSION=$(version_bumper get --text --project)
    ➤ echo $PROJECT_VERSION
    0.1.1

Setting the version(s) in the pyproject is simple:

    ➤ version_bumper version "1.2.3a4+54321" --json
    {"version": "1.2.3a4+54321"}

Setting the prerelease part of the version without change any other part:

    ➤ version_bumper set a 5 --json
    {"version": "1.2.3a5+54321"}

Now let's say we want to bump the pre-release (a5):

    ➤ version_bumper bump a --json
    {"version": "1.2.3a6"}

Notice bumping clears everything to the right, unless you are bumping the epoch:

    ➤ version_bumper bump epoch
    version: 1!1.2.3a6

The set command can optional clear everything to the right:

    ➤ version_bumper bump dev
    version: 1!1.2.3a6.dev1
    ➤ version_bumper set local "foo0123"
    version: 1!1.2.3a6.dev1+foo0123
    ➤ version_bumper set minor 4
    version: 1!1.4.3a6.dev1+foo0123
    ➤ version_bumper set minor 5 --clear-right
    version: 1!1.5.0

Let's set the epoch back to 0:

    ➤ version_bumper set epoch 0
    version: 1.5.0

And now make it a release candidate:

    ➤ version_bumper bump rc --json
    {"version": "1.5.0rc1"}

Finally let's make it the release version:

    ➤ version_bumper release --json
    {"version": "1.5.0"}

Please see the unit tests in tests/ directory for more examples.

## Installation

### PyPI Installation

`pip install version_bumper`

### Development Installation

#### Development Prerequisites

- Install the task manager: [Task](https://taskfile.dev/)
- Optionally install [pyenv-installer](https://github.com/pyenv/pyenv-installer)

  - Install dependent pythons, example:

    `pyenv local 3.11.9 3.12.3`

  _Note you may need to install some libraries for the pythons to compile
  cleanly._ _For example on ubuntu (note I prefer `nala` over `apt`):_

  `sudo nala install tk-dev libbz2-dev libreadline-dev libsqlite3-dev lzma-dev python3-tk libreadline-dev`

- Recommended to upgrade pip to latest.
- Optionally install [Poetry](https://python-poetry.org/)
- Optionally install [Hatch](https://hatch.pypa.io/)
- Optionally install [setuptools](https://setuptools.pypa.io/)
  - Install [build](https://build.pypa.io/)

Install the package using your favorite dev tool. Examples:

- `git clone git@github.com:royw/version_bumper.git`
- `cd version_bumper`
- `task init`
- `task make`

_Note, `task init` will run `git init .`, `git add` the initial project files,
and do a `git commit`. If you are using another VCS, please first edit the init
task in the `Taskfile.yaml` file._

See the [Developer README](DEV-README.md) for detailed information on the
development environment.

## License

`version_bumper` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.

## References

- The [Python Packaging User Guide](https://packaging.python.org/en/latest)
- The
  [pyproject.toml specification](https://pypi.python.org/pypi/pyproject.toml)
- The [Poetry pyproject.toml metadata](https://python-poetry.org/docs/pyproject)
- [pip documentation](https://pip.pypa.io/en/stable/)
- [Setuptools](https://setuptools.pypa.io/)
