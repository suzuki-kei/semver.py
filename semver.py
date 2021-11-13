"""
    Semantic Versioning 2.0.0 を扱うための機能を提供します.

    References
    ----------
     * Semantic Versioning (https://semver.org/)
"""


import itertools
import re
import typing


VersionMajor = int
"""
    メジャーバージョン.
    Ex. 1
"""


VersionMinor = int
"""
    マイナーバージョン.
    Ex. 2
"""


VersionPatch = int
"""
    パッチバージョン.
    Ex. 3
"""


VersionPreRelease = str|None
"""
    プレリリースバージョン.
    Ex. "alpha"
"""


VersionBuild = str|None
"""
    ビルドメタデータ.
    Ex. "build+777"
"""


VersionTuple = tuple[VersionMajor, VersionMinor, VersionPatch, VersionPreRelease, VersionBuild]
"""
    バージョン情報を保持するタプル.
    Ex. (1, 2, 3, "alpha", "build-777")
"""


VersionString = str
"""
    バージョン文字列.
    Ex. "1.2.3-alpha+build-777"
"""


class VersionError(ValueError):
    """
        無効なバージョンを指定されたことを意味する例外.
    """


class Version(object):
    """
        バージョン.
    """

    _VERSION_PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
    """
        バージョン文字列にマッチするパターン.
        ref https://semver.org/
    """

    _VERSION_PRE_RELEASE_PATTERN = re.compile(
        r"^(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)$")
    """
        パッチバージョンにマッチするパターン.
    """

    _VERSION_BUILD_PATTERN = re.compile(
        r"^(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)$")
    """
        ビルドメタデータにマッチするパターン.
    """

    @classmethod
    def from_string(self, version_string: VersionString) -> "Version":
        """
            バージョン文字列から Version を生成する.

            Arguments
            ---------
            version_string: VersionString
                バージョン文字列.

            Returns
            -------
            Version
                バージョン.

            Raises
            ------
            VersionError
                無効なバージョンの場合.
        """
        if match := self._VERSION_PATTERN.fullmatch(version_string):
            major, minor, patch, pre_release, build = match.groups()
            return self(int(major), int(minor), int(patch), pre_release, build)
        else:
            raise VersionError("illegal version", version_string)

    @classmethod
    def _validate_version(
            self,
            major: VersionMajor,
            minor: VersionMinor,
            patch: VersionPatch,
            pre_release: VersionPreRelease = None,
            build: VersionBuild = None
            ) -> None:
        """
            有効なバージョンであることを検証する.

            Arguments
            ---------
            major: VersionMajor
                メジャーバージョン.
            minor: VersionMinor
                マイナーバージョン.
            patch: VersionPatch
                パッチバージョン.
            pre_release: VersionPreRelease = None
                プレリリースバージョン.
            build: VersionBuild = None
                ビルドメタデータ.

            Raises
            ------
            VersionError
                無効なバージョンの場合.
        """
        is_valid_version = \
            (major >= 0) and \
            (minor >= 0) and \
            (patch >= 0) and \
            (pre_release is None or self._VERSION_PRE_RELEASE_PATTERN.fullmatch(pre_release)) and \
            (build is None or self._VERSION_BUILD_PATTERN.fullmatch(build))
        if not is_valid_version:
            version_tuple = (major, minor, patch, pre_release, build)
            raise VersionError("illegal version", version_tuple)

    @classmethod
    def _compare_version(
            self,
            version1: "Version",
            version2: "Version"
            ) -> int:
        """
            バージョンを比較する.

            Arguments
            ---------
            version1: Version
                左辺とするバージョン.
            version2: Version
                右辺とするバージョン.

            Returns
            -------
            int
                version1 == version2 の場合は 0.
                version1 < version2 の場合は負数.
                version1 > version2 の場合は正数.
        """
        version_core1 = (version1.major, version1.minor, version1.patch)
        version_core2 = (version2.major, version2.minor, version2.patch)
        if version_core1 < version_core2:
            return -1
        if version_core1 > version_core2:
            return +1

        pre_release1 = version1.pre_release
        pre_release2 = version2.pre_release
        return self._compare_version_pre_release(pre_release1, pre_release2)

    @classmethod
    def _compare_version_pre_release(
            self,
            pre_release1: VersionPreRelease,
            pre_release2: VersionPreRelease
            ) -> int:
        """
            プレリリースバージョンを比較する.

            Arguments
            ---------
            pre_release1: VersionPreRelease
                左辺とするプレリリースバージョン.
            pre_release2: VersionPreRelease
                右辺とするプレリリースバージョン.

            Returns
            -------
            int
                pre_release1 == pre_release2 の場合は 0.
                pre_release1 < pre_release2 の場合は負数.
                pre_release1 > pre_release2 の場合は正数.
        """
        if pre_release1 == pre_release2:
            return 0
        if pre_release1 is None:
            return +1
        if pre_release2 is None:
            return -1

        values1 = pre_release1.split(".")
        values2 = pre_release2.split(".")
        is_number_string = lambda value: re.fullmatch("\d+", value)

        for value1, value2 in itertools.zip_longest(values1, values2, fillvalue=""):
            if is_number_string(value1) and is_number_string(value2):
                value1 = int(value1)
                value2 = int(value2)
            if value1 < value2:
                return -1
            if value1 > value2:
                return +1
        return 0

    def __init__(
            self,
            major: VersionMajor,
            minor: VersionMinor,
            patch: VersionPatch,
            pre_release: VersionPreRelease = None,
            build: VersionBuild = None
            ) -> None:
        """
            インスタンスを初期化する.

            Arguments
            ---------
            major: VersionMajor
                メジャーバージョン.
            minor: VersionMinor
                マイナーバージョン.
            patch: VersionPatch
                パッチバージョン.
            pre_release: VersionPreRelease = None
                プレリリースバージョン.
            build: VersionBuild = None
                ビルドメタデータ.

            Raises
            ------
            VersionError
                無効なバージョンの場合.
        """
        self._validate_version(major, minor, patch, pre_release, build)
        self._major = major
        self._minor = minor
        self._patch = patch
        self._pre_release = pre_release
        self._build = build

    def __str__(self) -> str:
        return "{:d}.{:d}.{:d}{:s}{:s}".format(
            self._major,
            self._minor,
            self._patch,
            "" if self._pre_release is None else "-" + self._pre_release,
            "" if self._build is None else "+" + self._build)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        values = repr(tuple(self))
        return "{:s}{:s}".format(name, values)

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __iter__(self) -> typing.Iterable[VersionTuple]:
        return iter((
            self._major,
            self._minor,
            self._patch,
            self._pre_release,
            self._build,
        ))

    def __eq__(self, other) -> bool:
        return tuple(self) == tuple(other)

    def __ne__(self, other) -> bool:
        return tuple(self) != tuple(other)

    def __lt__(self, other) -> bool:
        return self._compare_version(self, other) < 0

    def __le__(self, other) -> bool:
        return self._compare_version(self, other) <= 0

    def __gt__(self, other) -> bool:
        return self._compare_version(self, other) > 0

    def __ge__(self, other) -> bool:
        return self._compare_version(self, other) >= 0

    @property
    def major(self) -> VersionMajor:
        """
            メジャーバージョンを取得する.

            Returns
            -------
            VersionMajor
                メジャーバージョン.
        """
        return self._major

    @property
    def minor(self) -> VersionMinor:
        """
            マイナーバージョンを取得する.

            Returns
            -------
            VersionMinor
                マイナーバージョン.
        """
        return self._minor

    @property
    def patch(self) -> VersionPatch:
        """
            パッチバージョンを取得する.

            Returns
            -------
            VersionPatch
                パッチバージョン.
        """
        return self._patch

    @property
    def pre_release(self) -> VersionPreRelease:
        """
            プレリリースバージョンを取得する.

            Returns
            -------
            VersionPreRelease
                プレリリースバージョン.
        """
        return self._pre_release

    @property
    def build(self) -> VersionBuild:
        """
            ビルドメタデータを取得する.

            Returns
            -------
            VersionBuild
                ビルドメタデータ.
        """
        return self._build

    def bump_major(
            self,
            *,
            keep_pre_release: bool = False,
            keep_build: bool = False
            ) -> "Version":
        """
            メジャーバージョンを上げる.

            Arguments
            ---------
            keep_pre_release: bool = False
                True を指定すると, プレリリースバージョンを維持する.
                False を指定すると, プレリリースバージョンは None となる.
            keep_build: bool = False
                True を指定すると, ビルドメタデータを維持する.
                False を指定すると, ビルドメタデータは None となる.

            Returns
            -------
            Version
                新しく生成したバージョン.
        """
        return self.__class__(
            self.major + 1,
            0,
            0,
            self.pre_release if keep_pre_release else None,
            self.build if keep_build else None)

    def bump_minor(
            self,
            *,
            keep_pre_release: bool = False,
            keep_build: bool = False
            ) -> "Version":
        """
            マイナーバージョンを上げる.

            Arguments
            ---------
            keep_pre_release: bool = False
                True を指定すると, プレリリースバージョンを維持する.
                False を指定すると, プレリリースバージョンは None となる.
            keep_build: bool = False
                True を指定すると, ビルドメタデータを維持する.
                False を指定すると, ビルドメタデータは None となる.

            Returns
            -------
            Version
                新しく生成したバージョン.
        """
        return self.__class__(
            self.major,
            self.minor + 1,
            0,
            self.pre_release if keep_pre_release else None,
            self.build if keep_build else None)

    def bump_patch(
            self,
            *,
            keep_pre_release: bool = False,
            keep_build: bool = False
            ) -> "Version":
        """
            パッチバージョンを上げる.

            Arguments
            ---------
            keep_pre_release: bool = False
                True を指定すると, プレリリースバージョンを維持する.
                False を指定すると, プレリリースバージョンは None となる.
            keep_build: bool = False
                True を指定すると, ビルドメタデータを維持する.
                False を指定すると, ビルドメタデータは None となる.

            Returns
            -------
            Version
                新しく生成したバージョン.
        """
        return self.__class__(
            self.major,
            self.minor,
            self.patch + 1,
            self.pre_release if keep_pre_release else None,
            self.build if keep_build else None)

    def bump_pre_release(
            self,
            pre_release: VersionPreRelease
            ) -> "Version":
        """
            プレリリースバージョンを設定する.

            Arguments
            ---------
            pre_release: VersionPreRelease
                プレリリースバージョン.

            Returns
            -------
            Version
                新しく生成したバージョン.

            Raises
            ------
            VersionError
                無効なプレリリースバージョンの場合.
        """
        return self.__class__(
            self.major,
            self.minor,
            self.patch,
            pre_release,
            self.build)

    def bump_build(
            self,
            build: VersionBuild
            ) -> "Version":
        """
            ビルドメタデータを設定する.

            Arguments
            ---------
            build: VersionBuild
                ビルドメタデータ.

            Returns
            -------
            Version
                新しく生成したバージョン.

            Raises
            ------
            VersionError
                無効なビルドメタデータの場合.
        """
        return self.__class__(
            self.major,
            self.minor,
            self.patch,
            self.pre_release,
            build)

