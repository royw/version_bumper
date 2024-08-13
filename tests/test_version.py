# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

from version_bumper.version import Version


def test_version_roundtrip() -> None:
    """string to Version to string"""
    assert str(Version("1")) == "1", "release N"
    assert str(Version("0.1")) == "0.1", "release N.N"
    assert str(Version("0.1.0")) == "0.1.0", "release N.N.N"
    assert str(Version("2!0.1.0")) == "2!0.1.0", "epoch N!N.N.N"
    assert str(Version("0.1.0a1")) == "0.1.0a1", "pre N.N.NaN"
    assert str(Version("0.1.0b1")) == "0.1.0b1", "pre N.N.NaN"
    assert str(Version("0.1.0rc1")) == "0.1.0rc1", "pre N.N.NaN"
    assert str(Version("0.1.0.post2")) == "0.1.0.post2", "post N.N.N.postN"
    assert str(Version("0.1.0a3.post2")) == "0.1.0a3.post2", "pre post N.N.N{a|b|rc}N.postN"
    assert str(Version("0.1.0b13.post2")) == "0.1.0b13.post2", "pre post N.N.N{a|b|rc}N.postN"
    assert str(Version("0.1.0rc123.post2")) == "0.1.0rc123.post2", "pre post N.N.N{a|b|rc}N.postN"
    assert str(Version("0.1.0.dev3")) == "0.1.0.dev3", "dev N.N.N.devN"
    assert str(Version("0.1.0.dev3+41")) == "0.1.0.dev3+41", "dev local N.N.N.devN+N"
    assert (
        str(Version("1!0.1.0rc123.post2.dev4+41ax")) == "1!0.1.0rc123.post2.dev4+41ax"
    ), "epoch release pre post dev local N!N.N.N{a|b|rc}N.postN.devN+local"


def test_less_than() -> None:
    assert Version("1") < Version("2")
    assert Version("0.1") < Version("0.1.1")
    assert Version("0.1.1") < Version("0.1.11")
    assert Version("0.1.0") < Version("1!0.1.0")
    assert Version("2!0.1.0") < Version("2!0.1.1")
    assert Version("2!0.1.0") < Version("3!0.1.0")
    assert Version("0.1.0a1") < Version("0.1.0a2")
    assert Version("0.1.0a1") < Version("0.1.0b1")
    assert Version("0.1.0rc1") < Version("0.1.1rc1")
    assert Version("0.1.0.post2") < Version("0.1.0.post3")
    assert Version("0.1.0a3.post2") < Version("0.1.0a4.post2")
    assert Version("0.1.0b13.post2") < Version("0.1.0b13.post4")
    assert Version("0.1.0rc123.post2") < Version("0.1.1rc123.post2")
    assert Version("0.1.0rc123.post2") < Version("0.2.0rc123.post2")
    assert Version("0.1.0rc123.post2") < Version("1.1.0rc123.post2")
    assert Version("0.1.0.dev3") < Version("0.1.1.dev3")
    assert Version("0.1.0.dev3") < Version("0.1.0.dev4")
    assert Version("0.1.0.dev3+40") < Version("0.1.0.dev3+41")
    assert Version("1!0.1.0rc123.post2.dev4+41ax") < Version("1!0.1.0rc123.post2.dev4+41bx")


def test_equal() -> None:
    assert Version("1") == Version("1")
    assert Version("0.1") == Version("0.1")
    assert Version("0.1.1") == Version("0.1.1")
    assert Version("2!0.1.0") == Version("2!0.1.0")
    assert Version("0.1.0a1") == Version("0.1.0a1")
    assert Version("0.1.0b1") == Version("0.1.0b1")
    assert Version("0.1.0rc1") == Version("0.1.0rc1")
    assert Version("0.1.0.post2") == Version("0.1.0.post2")
    assert Version("0.1.0a3.post2") == Version("0.1.0a3.post2")
    assert Version("0.1.0rc123.post2") == Version("0.1.0rc123.post2")
    assert Version("0.1.0.dev3") == Version("0.1.0.dev3")
    assert Version("0.1.0.dev3+41") == Version("0.1.0.dev3+41")
    assert Version("1!0.1.0rc123.post2.dev4+41ax") == Version("1!0.1.0rc123.post2.dev4+41ax")


def test_bump() -> None:
    assert Version("1").bump(part="local") == Version("1+1")
    assert Version("1.2.3+40").bump(part="local") == Version("1.2.3+41")
    assert Version("1").bump(part="epoch") == Version("1!1")
    assert Version("1!1").bump(part="epoch") == Version("2!1")
    assert Version("1").bump(part="major") == Version("2")
    assert Version("1").bump(part="minor") == Version("1.1")
    assert Version("1").bump(part="patch") == Version("1.0.1")
    assert Version("1").bump(part="a") == Version("1a1")
    assert Version("1a1").bump(part="a") == Version("1a2")
    assert Version("1").bump(part="b") == Version("1b1")
    assert Version("1").bump(part="rc") == Version("1rc1")
    assert Version("1rc1").bump(part="rc") == Version("1rc2")
    assert Version("1").bump(part="post") == Version("1.post1")
    assert Version("1.post1").bump(part="post") == Version("1.post2")
    assert Version("1").bump(part="dev") == Version("1.dev1")
    assert Version("1.dev1").bump(part="dev") == Version("1.dev2")
    assert Version("1.2.3").bump(part="rc") == Version("1.2.3rc1")


def test_bump_release() -> None:
    assert str(Version("1.0.rc1").bump_release()) == "1.0"
    assert str(Version("1.0.rc1.dev1").bump_release()) == "1.0"
    assert str(Version("1.0.rc1.post2").bump_release()) == "1.0"
    assert str(Version("1.0.rc1+foo3").bump_release()) == "1.0"
    assert str(Version("1.0.rc1.post3.dev4+foo5").bump_release()) == "1.0"


def test_set() -> None:
    assert str(Version("1.2").set(part="epoch", value="2")) == "2!1.2"
    assert str(Version("1.2").set(part="major", value="2")) == "2.2"
    assert str(Version("1.2").set(part="major", value="2", clear_right=True)) == "2.0"
    assert str(Version("1.2").set(part="minor", value="5")) == "1.5"
    assert str(Version("1.2.3-rc2").set(part="minor", value="5")) == "1.5.3rc2"
    assert str(Version("1.2-rc2").set(part="minor", value="5")) == "1.5rc2"
    assert str(Version("1.2-rc2").set(part="minor", value="5", clear_right=False)) == "1.5rc2"
    assert str(Version("1.2-rc2").set(part="minor", value="5", clear_right=True)) == "1.5"
    assert str(Version("1.2").set(part="major", value="2")) == "2.2"

    assert str(Version("1.2").set(part="local", value="foo0100")) == "1.2+foo0100"
    assert str(Version("1.2").set(part="dev", value="dev")) == "1.2.dev0"
    assert str(Version("1.2").set(part="dev", value="")) == "1.2"  # setting to empty string clears part value
    assert str(Version("1.2").set(part="rc", value="")) == "1.2rc0"


def test_normalizations() -> None:
    assert str(Version("1.2.3")) == "1.2.3"
    assert str(Version("1.2.3.a")) == "1.2.3a0"
    assert str(Version("1.2.3.a1")) == "1.2.3a1"
    assert str(Version("1.2.3.a01")) == "1.2.3a1"
    assert str(Version("1.2.3alpha1")) == "1.2.3a1"
    assert str(Version("1.2.3beta1")) == "1.2.3b1"
    assert str(Version("1.2.3c1")) == "1.2.3rc1"
    assert str(Version("1.2.3pre1")) == "1.2.3rc1"
    assert str(Version("1.2.3preview1")) == "1.2.3rc1"
    assert str(Version("1.2.3preview")) == "1.2.3rc0"
    assert str(Version("1.2.3.A")) == "1.2.3a0"
    assert str(Version("1.2.3.A1")) == "1.2.3a1"
    assert str(Version("1.2.3.A01")) == "1.2.3a1"
    assert str(Version("1.2.3Alpha1")) == "1.2.3a1"
    assert str(Version("1.2.3BETA1")) == "1.2.3b1"
    assert str(Version("1.2.3C1")) == "1.2.3rc1"
    assert str(Version("1.2.3PRE1")) == "1.2.3rc1"
    assert str(Version("1.2.3Preview1")) == "1.2.3rc1"
    assert str(Version("1.2.3PREVIEW")) == "1.2.3rc0"


def test_prerelease_separators() -> None:
    assert str(Version("1.1a")) == "1.1a0"
    assert str(Version("1.1.a")) == "1.1a0"
    assert str(Version("1.1-a")) == "1.1a0"
    assert str(Version("1.1_a")) == "1.1a0"
    assert str(Version("1.1a.2")) == "1.1a2"
    assert str(Version("1.1a-2")) == "1.1a2"
    assert str(Version("1.1a_2")) == "1.1a2"


def test_postrelease_separators() -> None:
    assert str(Version("1.2.3.post1")) == "1.2.3.post1"
    assert str(Version("1.2.3.post.1")) == "1.2.3.post1"
    assert str(Version("1.2.3.post-1")) == "1.2.3.post1"
    assert str(Version("1.2.3.post_1")) == "1.2.3.post1"
    assert str(Version("1.2.3-post1")) == "1.2.3.post1"
    assert str(Version("1.2.3-post.1")) == "1.2.3.post1"
    assert str(Version("1.2.3-post-1")) == "1.2.3.post1"
    assert str(Version("1.2.3-post_1")) == "1.2.3.post1"
    assert str(Version("1.2.3_post1")) == "1.2.3.post1"
    assert str(Version("1.2.3_post.1")) == "1.2.3.post1"
    assert str(Version("1.2.3_post-1")) == "1.2.3.post1"
    assert str(Version("1.2.3_post_1")) == "1.2.3.post1"
    assert str(Version("1.2.3.post")) == "1.2.3.post0"
    assert str(Version("1.2.3-post")) == "1.2.3.post0"
    assert str(Version("1.2.3_post")) == "1.2.3.post0"
    assert str(Version("1.2.3-1")) == "1.2.3.post1"


def test_dev_separators() -> None:
    assert str(Version("1.2.3.dev1")) == "1.2.3.dev1"
    assert str(Version("1.2.3-dev1")) == "1.2.3.dev1"
    assert str(Version("1.2.3_dev1")) == "1.2.3.dev1"
    assert str(Version("1.2.3dev1")) == "1.2.3.dev1"
    assert str(Version("1.2.3.dev.1")) == "1.2.3.dev1"
    assert str(Version("1.2.3-dev-1")) == "1.2.3.dev1"
    assert str(Version("1.2.3_dev_1")) == "1.2.3.dev1"
    assert str(Version("1.2.3dev")) == "1.2.3.dev0"


def test_whitespaces() -> None:
    assert str(Version(" 1.2.3")) == "1.2.3"
    assert str(Version("\t1.2.3.a")) == "1.2.3a0"
    assert str(Version("\n1.2.3.a1")) == "1.2.3a1"
    assert str(Version("\r1.2.3.a01")) == "1.2.3a1"
    assert str(Version("\f1.2.3alpha1")) == "1.2.3a1"
    assert str(Version("\v1.2.3beta1")) == "1.2.3b1"
    assert str(Version("1.2.3c1 ")) == "1.2.3rc1"
    assert str(Version("1.2.3pre1\t")) == "1.2.3rc1"
    assert str(Version("1.2.3preview1\n")) == "1.2.3rc1"
    assert str(Version("1.2.3preview\r")) == "1.2.3rc0"
    assert str(Version("1.2.3preview1\f")) == "1.2.3rc1"
    assert str(Version("1.2.3preview1\v")) == "1.2.3rc1"
    assert str(Version(" \t\n\r\f\v1.2.3preview1 \t\n\r\f\v")) == "1.2.3rc1"


def test_v_prefix() -> None:
    assert str(Version("v1.2.3.dev1")) == "1.2.3.dev1"
    assert str(Version("V1.1")) == "1.1"


def test_local() -> None:
    assert str(Version("v1.2.3+foo")) == "1.2.3+foo"
    assert str(Version("v1.2.3+foo0100")) == "1.2.3+foo0100"
    assert str(Version("v1.2.3+ubuntu.1")) == "1.2.3+ubuntu.1"
    assert str(Version("v1.2.3+ubuntu-1")) == "1.2.3+ubuntu.1"
    assert str(Version("v1.2.3+ubuntu_1")) == "1.2.3+ubuntu.1"


def test_major_minor() -> None:
    for version_value in range(1, 12):
        version_str = f"0.{version_value}"
        assert str(Version(version_str)) == version_str
        assert str(Version(version_str).bump(part="minor")) == f"0.{version_value + 1}"


def test_major_minor_micro() -> None:
    assert str(Version("1.1.0")) == "1.1.0"
    assert str(Version("1.1.1").bump(part="patch")) == "1.1.2"
    assert str(Version("1.1.2").bump(part="minor")) == "1.2.0"


def test_major_minor_pre() -> None:
    assert str(Version("0.9").bump(part="major")) == "1.0"
    assert str(Version("1.0").bump(part="a")) == "1.0a1"
    assert str(Version("1.0a1").bump(part="a")) == "1.0a2"
    assert str(Version("1.0a2").bump(part="b")) == "1.0b1"
    assert str(Version("1.01").bump(part="rc")) == "1.1rc1"
    assert str(Version("1.0.rc1").bump_release()) == "1.0"
    assert str(Version("1.1a1")) == "1.1a1"


def test_major_minor_post() -> None:
    assert str(Version("0.9")) == "0.9"
    assert str(Version("1.0.dev1")) == "1.0.dev1"
    assert str(Version("1.0.dev2")) == "1.0.dev2"
    assert str(Version("1.0.dev3")) == "1.0.dev3"
    assert str(Version("1.0.dev4")) == "1.0.dev4"
    assert str(Version("1.0c1")) == "1.0rc1"  # c promoted to rc
    assert str(Version("1.0c2")) == "1.0rc2"  # c promoted to rc
    assert str(Version("1.0")) == "1.0"
    assert str(Version("1.0.post1")) == "1.0.post1"
    assert str(Version("1.1.dev1")) == "1.1.dev1"


def test_date_versions() -> None:
    assert str(Version("2012.1")) == "2012.1"
    assert str(Version("2012.2")) == "2012.2"
    assert str(Version("2012.3")) == "2012.3"
    assert str(Version("2012.15")) == "2012.15"
    assert str(Version("2013.1")) == "2013.1"
    assert str(Version("2013.2")) == "2013.2"


def test_possible_combinations() -> None:
    assert str(Version("1.dev0")) == "1.dev0"
    assert str(Version("1.0.dev456")) == "1.0.dev456"
    assert str(Version("1.0a1")) == "1.0a1"
    assert str(Version("1.0a2.dev456")) == "1.0a2.dev456"
    assert str(Version("1.0a12.dev456")) == "1.0a12.dev456"
    assert str(Version("1.0a12")) == "1.0a12"
    assert str(Version("1.0b1.dev456")) == "1.0b1.dev456"
    assert str(Version("1.0b2")) == "1.0b2"
    assert str(Version("1.0b2.post345.dev456")) == "1.0b2.post345.dev456"
    assert str(Version("1.0b2.post345")) == "1.0b2.post345"
    assert str(Version("1.0rc1.dev456")) == "1.0rc1.dev456"
    assert str(Version("1.0rc1")) == "1.0rc1"
    assert str(Version("1.0")) == "1.0"
    assert str(Version("1.0+abc.5")) == "1.0+abc.5"
    assert str(Version("1.0+abc.7")) == "1.0+abc.7"
    assert str(Version("1.0+5")) == "1.0+5"
    assert str(Version("1.0.post456.dev34")) == "1.0.post456.dev34"
    assert str(Version("1.0.post456")) == "1.0.post456"
    assert str(Version("1.0.15")) == "1.0.15"
    assert str(Version("1.1.dev1")) == "1.1.dev1"


def test_invalid_version() -> None:
    with pytest.raises(ValueError, match="Invalid version string"):
        assert str(Version("1.2.3.")) == "1.2.3"


def test_invalid_part_bump() -> None:
    version = Version("1.2.3")
    assert str(version.bump(part="minor")) == "1.3.0"
    with pytest.raises(ValueError, match="Invalid part value"):
        version.bump(part="foobar")


def test_none_less_than_none() -> None:
    # force error conditions

    # both minors are None
    ver1 = Version("1")
    ver2 = Version("1")
    ver1.minor = None
    ver2.minor = None
    assert not ver1 < ver2
    assert ver1 == ver2

    # int is not less than None
    ver1 = Version("1")
    ver2 = Version("1")
    ver1.minor = 0
    ver2.minor = None
    assert not ver1 < ver2
    assert ver1 != ver2

    ver1 = Version("1")
    ver2 = Version("1")
    ver1.minor = 1
    ver2.minor = None
    assert not ver1 < ver2
    assert ver1 != ver2

    # None is less than int
    ver1 = Version("1")
    ver2 = Version("1")
    ver1.minor = None
    ver2.minor = 0
    assert ver1 < ver2
    assert ver1 != ver2

    ver1 = Version("1")
    ver2 = Version("1")
    ver1.minor = None
    ver2.minor = 1
    assert ver1 < ver2


def test_set_invalid_part() -> None:
    ver = Version("1.2.3")
    ver.set(part="foo", value="4")  # can't set unsupported part
    assert str(ver) == "1.2.3"
