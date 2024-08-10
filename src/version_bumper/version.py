# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import functools
import re
from collections.abc import Sequence
from typing import Any, Self

"""
A comparable Version object that fully conforms to the PYPA version specification in:
https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers

Usage example:

    version = Version('1.2.2')              # 1.2.2
    version.bump(part=minor")               # 1.2.3
    version.bump(part="dev")                # 1.2.3.dev1
    version.bump(part="rc")                 # 1.2.3.rc1
    version.bump(part="dev")                # 1.2.3.rc1.dev1
    version.set(part="local", "foo0100")    # 1.2.3.rc1.dev1+foo0100
    version.bump(part="local")              # 1.2.3.rc1.dev1+foo0101
    version.bump_release()                  # 1.2.3
"""

# functools.total_ordering
# Given a class defining one or more rich comparison ordering methods, this class decorator supplies the rest.
# This simplifies the effort involved in specifying all the possible rich comparison operations:
#
# The class must define one of __lt__(), __le__(), __gt__(), or __ge__(). In addition, the class should supply
# an __eq__() method.


@functools.total_ordering
class Version:
    PARTS: Sequence[str] = ("epoch", "major", "minor", "patch", "a", "b", "rc", "post", "dev", "local")
    PARSED_PARTS: Sequence[str] = ("epoch", "major", "minor", "patch", "pre", "post", "dev", "local")
    PRE_PARTS: Sequence[str] = ("a", "b", "c", "rc", "alpha", "beta", "pre", "preview")
    POST_PARTS: Sequence[str] = ("r", "rev", "post")
    INT_PARTS: Sequence[str] = ("epoch", "major", "minor", "patch")

    # This version parsing regex is from:
    # https://packaging.python.org/en/latest/specifications/version-specifiers/#appendix-parsing-version-strings-with-regular-expressions
    VERSION_PATTERN = r"""
        v?
        (?:
            (?:(?P<epoch>[0-9]+)!)?                           # epoch
            (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
            (?P<pre>                                          # pre-release
                [-_\.]?
                (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
                [-_\.]?
                (?P<pre_n>[0-9]+)?
            )?
            (?P<post>                                         # post release
                (?:-(?P<post_n1>[0-9]+))
                |
                (?:
                    [-_\.]?
                    (?P<post_l>post|rev|r)
                    [-_\.]?
                    (?P<post_n2>[0-9]+)?
                )
            )?
            (?P<dev>                                          # dev release
                [-_\.]?
                (?P<dev_l>dev)
                [-_\.]?
                (?P<dev_n>[0-9]+)?
            )?
        )
        (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
    """

    def __init__(self, version_str: str) -> None:
        """
        Parse the version string into normalized parts in the Version instance.
        """
        # Case sensitivity
        # All ascii letters should be interpreted case insensitively within a version and the normal
        # form is lowercase. This allows versions such as 1.1RC1 which would be normalized to 1.1rc1.
        #
        # Leading and Trailing Whitespace
        # Leading and trailing whitespace must be silently ignored and removed from all normalized forms of
        # a version. This includes " ", \t, \n, \r, \f, and \v. This allows accidental whitespace to be
        # handled sensibly, such as a version like 1.0\n which normalizes to 1.0.
        #
        # Preceding v character
        # In order to support the common version notation of v1.0 versions may be preceded by a single
        # literal v character. This character MUST be ignored for all purposes and should be omitted
        # from all normalized forms of the version. The same version with and without the v is considered
        # equivalent.
        self.version_str = version_str.lower().strip("\t\n\r\f\v").lstrip("v")

        # parse the version string using the PYPA regex
        _regex = re.compile(
            r"^\s*" + Version.VERSION_PATTERN + r"\s*$",
            re.VERBOSE | re.IGNORECASE,
        )
        match = _regex.match(self.version_str)
        if match is None:
            msg = f"Invalid version string: {self.version_str}"
            raise ValueError(msg)

        # normalize the parts
        self.epoch: int = int(match.group("epoch") or 0)
        self.release: str = match.group("release")
        release_parts: Sequence[int] = tuple(map(int, self.release.split(".")))
        self.major: int = release_parts[0] if len(release_parts) >= 1 else 0
        self.minor: int | None = release_parts[1] if len(release_parts) >= 2 else None
        self.patch: int | None = release_parts[2] if len(release_parts) >= 3 else None
        self.pre: str = self.__pre_normalize(match.group("pre") or "")
        self.post: str = self.__post_normalize(match.group("post") or "")
        self.dev: str = self.__dev_normalize(match.group("dev") or "")
        self.local: str = self.__local_normalize(match.group("local") or "")

    def __str__(self) -> str:
        """
        Convert from the version parts into a version string.
        """
        version_parts = []
        if int(self.epoch) > 0:
            version_parts.append(f"{self.epoch}!")
        version_parts.append(str(self.major))
        if self.minor is not None:
            version_parts.append(f".{self.minor}")
        if self.patch is not None:
            version_parts.append(f".{self.patch}")
        version_parts.append(self.pre)
        version_parts.append(self.post)
        version_parts.append(self.dev)
        if self.local:
            version_parts.append(f"+{self.local}")
        return "".join([str(v) for v in version_parts])

    def __lt__(self, other: Self) -> bool:
        """test if self is less than other"""

        # note, testing order is critical
        if self.epoch < other.epoch:
            return True
        if self.major < other.major:
            return True
        if self.__is_optional_value_less_than(self.minor, other.minor):
            return True
        if self.__is_optional_value_less_than(self.patch, other.patch):
            return True
        if self.pre < other.pre:
            return True
        if self.post < other.post:
            return True
        if self.dev < other.dev:
            return True
        return self.local < other.local

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def bump(self, part: str) -> Self:
        """Increment the given part of the version.
        Valid part values are in PARTS sequence.
        Bump the part if part is not None.
        Set the value to new_version if it is not None.
        return False if unable to modify.
        """
        if part not in Version.PARTS:
            msg = f"Invalid part value: {part}"
            raise ValueError(msg)

        self.epoch = self.__bump_int_part(part=part, prefix="epoch", value=self.epoch)
        self.major = self.__bump_int_part(part=part, prefix="major", value=self.major)
        self.minor = self.__bump_optional_int_part(part=part, prefix="minor", value=self.minor)
        if part == "patch":
            self.minor = int(self.minor or 0)
        self.patch = self.__bump_optional_int_part(part=part, prefix="patch", value=self.patch)
        self.pre = self.__bump_part(part=part, prefix="a", value=self.pre)
        self.pre = self.__bump_part(part=part, prefix="b", value=self.pre)
        self.pre = self.__bump_part(part=part, prefix="rc", value=self.pre)
        self.post = self.__bump_part(part=part, prefix=".post", value=self.post)
        self.dev = self.__bump_part(part=part, prefix=".dev", value=self.dev)
        if part == "local":
            self.local = str(int(self.local or 0) + 1)

        # clear parts to the right of the bumped part, except epoch
        if part != "epoch":
            part_index = Version.PARSED_PARTS.index(self.__part_to_parsed_part(part))
            self.__clear_parts(Version.PARSED_PARTS[part_index + 1 :])

        return self

    def bump_release(self) -> Self:
        """
        Remove any pre, dev, local parts.  Basically prepare the release version.
        """
        self.__clear_parts(["pre", "post", "dev", "local"])
        return self

    def set(self, part: str, value: str, clear_right: bool = False) -> Self:
        if part and part in Version.PARTS:
            if part in Version.PRE_PARTS:
                value = f"{part}{value}"
                part = "pre"
                setattr(self, part, self.__pre_normalize(value))
            elif part in Version.POST_PARTS:
                part = "post"
                setattr(self, part, self.__post_normalize(value))
            elif part == "local":
                setattr(self, part, self.__local_normalize(value))
            elif part == "dev":
                setattr(self, part, f"dev{int(value)}")
            elif part in Version.INT_PARTS:
                setattr(self, part, int(value))
            if clear_right:
                parts_to_clear_slice = slice(Version.PARSED_PARTS.index(part) + 1, None)
                self.__clear_parts(Version.PARSED_PARTS[parts_to_clear_slice])
        return self

    @staticmethod
    def __part_to_parsed_part(part: str) -> str:
        if part in Version.PRE_PARTS:
            part = "pre"
        elif part in Version.POST_PARTS:
            part = "post"
        return part

    @staticmethod
    def __implicit_release(release: str) -> str:
        """
        Implicit pre-release number
        Pre releases allow omitting the numeral in which case it is implicitly assumed to be 0. The normal
        form for this is to include the 0 explicitly. This allows versions such as 1.2a which is normalized
        to 1.2a0.
        """
        match = re.match(r"(.*\D)(\d+)$", release)
        if match:
            prefix = match.group(1)
            value = int(match.group(2))
            release = f"{prefix}{value}"
        else:
            release = f"{release}0"
        return release

    @staticmethod
    def __pre_normalize(release: str) -> str:
        """
        Pre-release separators
        Pre-releases should allow a ., -, or _ separator between the release segment and the pre-release
        segment. The normal form for this is without a separator. This allows versions such as 1.1.a1
        or 1.1-a1 which would be normalized to 1.1a1. It should also allow a separator to be used
        between the pre-release signifier and the numeral. This allows versions such as 1.0a.1 which
        would be normalized to 1.0a1.

        Pre-release spelling
        Pre-releases allow the additional spellings of alpha, beta, c, pre, and preview for a, b, rc, rc,
        and rc respectively. This allows versions such as 1.1alpha1, 1.1beta2, or 1.1c3 which normalize
        to 1.1a1, 1.1b2, and 1.1rc3. In every case the additional spelling should be considered
        equivalent to their normal forms.

        Implicit pre-release number
        Pre releases allow omitting the numeral in which case it is implicitly assumed to be 0. The normal
        form for this is to include the 0 explicitly. This allows versions such as 1.2a which is normalized to 1.2a0.
        """
        if release:
            release = release.replace(".", "")
            release = release.replace("-", "")
            release = release.replace("_", "")
            release = release.replace("alpha", "a")
            release = release.replace("beta", "b")
            release = release.replace("c", "rc") if release.startswith("c") else release
            release = release.replace("preview", "rc")
            release = release.replace("pre", "rc")
            if not release:
                release = "pre0"
            if all(characters.isdigit() for characters in release):
                release = f"pre{release}"
            release = Version.__implicit_release(release)
        return release

    @staticmethod
    def __post_normalize(release: str) -> str:
        """
        Post release separators
        Post releases allow a ., -, or _ separator as well as omitting the separator all together.
        The normal form of this is with the . separator. This allows versions such as 1.2-post2 or
        1.2post2 which normalize to 1.2.post2. Like the pre-release separator this also allows an
        optional separator between the post release signifier and the numeral. This allows versions
        like 1.2.post-2 which would normalize to 1.2.post2.

        Post release spelling
        Post-releases allow the additional spellings of rev and r. This allows versions such as 1.0-r4
        which normalizes to 1.0.post4. As with the pre-releases the additional spellings should be
        considered equivalent to their normal forms.

        Implicit post release number
        Post releases allow omitting the numeral in which case it is implicitly assumed to be 0. The
        normal form for this is to include the 0 explicitly. This allows versions such as 1.2.post
        which is normalized to 1.2.post0.
        """
        if release:
            if re.match(r"^[.\-_]", release):
                release = release[1:]
            release = release.replace(".", "")
            release = release.replace("-", "")
            release = release.replace("_", "")
            release = release.replace("rev", "post")
            release = release.replace("r", "post")
            if not release:
                release = "post0"
            if all(characters.isdigit() for characters in release):
                release = f"post{release}"
            release = Version.__implicit_release(release)
            release = f".{release}"
        return release

    @staticmethod
    def __dev_normalize(release: str) -> str:
        """
        Development release separators
        Development releases allow a ., -, or a _ separator as well as omitting the separator all together.
        The normal form of this is with the . separator. This allows versions such as 1.2-dev2 or 1.2dev2
        which normalize to 1.2.dev2.

        Implicit development release number
        Development releases allow omitting the numeral in which case it is implicitly assumed to be 0.
        The normal form for this is to include the 0 explicitly. This allows versions such as 1.2.dev
        which is normalized to 1.2.dev0.
        """
        if release:
            if re.match(r"^[.\-_]", release):
                release = release[1:]
            release = release.replace(".", "")
            release = release.replace("-", "")
            release = release.replace("_", "")
            if not release:
                release = "dev0"
            if all(characters.isdigit() for characters in release):
                release = f"dev{release}"
            release = Version.__implicit_release(release)
            release = f".{release}"
        return release

    @staticmethod
    def __local_normalize(release: str) -> str:
        """
        Local version segments
        With a local version, in addition to the use of . as a separator of segments, the use of - and _ is
        also acceptable. The normal form is using the . character. This allows versions such as
        1.0+ubuntu-1 to be normalized to 1.0+ubuntu.1.
        """
        if release:
            release = release.replace("-", ".")
            release = release.replace("_", ".")
        return release

    @staticmethod
    def __is_optional_value_less_than(value1: int | None, value2: int | None) -> bool:
        if value1 is None and value2 is None:
            return False
        if value1 is None:
            return True
        if value2 is None:
            return False
        return value1 < value2

    @staticmethod
    def __bump_part(part: str, prefix: str, value: str) -> str:
        if part and prefix and (prefix in {part, f".{part}"}):
            if value.startswith(prefix):
                return f"{prefix}{int(value[len(prefix):]) + 1}"
            return f"{prefix}1"
        return value

    @staticmethod
    def __bump_int_part(part: str, prefix: str, value: int) -> int:
        if part and prefix and part == prefix:
            value = (value or 0) + 1
        return value

    @staticmethod
    def __bump_optional_int_part(part: str, prefix: str, value: int | None) -> int | None:
        if part and prefix and part == prefix:
            value = (value or 0) + 1
        return value

    def __clear_parts(self, parts: Sequence[str]) -> None:
        if not contains(parts, Version.PARSED_PARTS):
            msg = f"Requires parsed parts ({Version.PARSED_PARTS}), given: {parts}"
            raise ValueError(msg)
        for part in parts:
            # do not clear major
            if part in ["epoch", "minor", "patch"]:
                if isinstance(getattr(self, part), int):
                    setattr(self, part, 0)
            elif part != "major":
                setattr(self, part, "")


def contains(small: Sequence[Any], big: Sequence[Any]) -> bool | tuple[int, int]:
    for i in range(len(big) - len(small) + 1):
        for j in range(len(small)):
            if big[i + j] != small[j]:
                break
        else:
            return i, i + len(small)
    return False
