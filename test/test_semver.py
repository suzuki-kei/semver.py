"""
    semver のテストケース.
"""


from semver import *
import itertools
import semver
import typing
import unittest


VALID_VERSION_MAJOR_VALUES: tuple[VersionMajor] = (
    0,
    1,
    2,
    3,
    10,
    777,
)


INVALID_VERSION_MAJOR_VALUES: tuple[VersionMajor] = (
    -1,
    -2,
    -3,
    -10,
    -777,
)


VALID_VERSION_MINOR_VALUES: tuple[VersionMinor] = (
    0,
    1,
    2,
    3,
    10,
    777,
)


INVALID_VERSION_MINOR_VALUES: tuple[VersionMinor] = (
    -1,
    -2,
    -3,
    -10,
    -777,
)


VALID_VERSION_PATCH_VALUES: tuple[VersionPatch] = (
    0,
    1,
    2,
    3,
    10,
    777,
)


INVALID_VERSION_PATCH_VALUES: tuple[VersionPatch] = (
    -1,
    -2,
    -3,
    -10,
    -777,
)


VALID_VERSION_PRE_RELEASE_VALUES: tuple[VersionPreRelease] = (
    None,
    "alpha",
    "beta",
    "rc.1",
)


INVALID_VERSION_PRE_RELEASE_VALUES: tuple[VersionPreRelease] = (
    "",
    "alpha+1",
    "alpha.01",
)


VALID_VERSION_BUILD_VALUES: tuple[VersionBuild] = (
    None,
    "build-777",
    "build.1.2.3",
)


INVALID_VERSION_BUILD_VALUES: tuple[VersionBuild] = (
    "",
    "build+777",
)


def _valid_versions() -> typing.Iterable[VersionTuple]:
    """
        有効なバージョン.

        Returns
        -------
        typing.Iterable[VersionTuple]
            VersionTuple を含む Iterable.
    """
    return itertools.product(
        VALID_VERSION_MAJOR_VALUES,
        VALID_VERSION_MINOR_VALUES,
        VALID_VERSION_PATCH_VALUES,
        VALID_VERSION_PRE_RELEASE_VALUES,
        VALID_VERSION_BUILD_VALUES,
    )


def _invalid_versions() -> typing.Iterable[VersionTuple]:
    """
        無効なバージョン.

        Returns
        -------
        typing.Iterable[VersionTuple]
            VersionTuple を含む Iterable.
    """
    return itertools.chain(
        # major だけが無効な値.
        itertools.product(
            INVALID_VERSION_MAJOR_VALUES,
            VALID_VERSION_MINOR_VALUES,
            VALID_VERSION_PATCH_VALUES,
            VALID_VERSION_PRE_RELEASE_VALUES,
            VALID_VERSION_BUILD_VALUES,
        ),
        # minor だけが無効な値.
        itertools.product(
            VALID_VERSION_MAJOR_VALUES,
            INVALID_VERSION_MINOR_VALUES,
            VALID_VERSION_PATCH_VALUES,
            VALID_VERSION_PRE_RELEASE_VALUES,
            VALID_VERSION_BUILD_VALUES,
        ),
        # patch だけが無効な値.
        itertools.product(
            VALID_VERSION_MAJOR_VALUES,
            VALID_VERSION_MINOR_VALUES,
            INVALID_VERSION_PATCH_VALUES,
            VALID_VERSION_PRE_RELEASE_VALUES,
            VALID_VERSION_BUILD_VALUES,
        ),
        # pre_release だけが無効な値.
        itertools.product(
            VALID_VERSION_MAJOR_VALUES,
            VALID_VERSION_MINOR_VALUES,
            VALID_VERSION_PATCH_VALUES,
            INVALID_VERSION_PRE_RELEASE_VALUES,
            VALID_VERSION_BUILD_VALUES,
        ),
        # build だけが無効な値.
        itertools.product(
            VALID_VERSION_MAJOR_VALUES,
            VALID_VERSION_MINOR_VALUES,
            VALID_VERSION_PATCH_VALUES,
            VALID_VERSION_PRE_RELEASE_VALUES,
            INVALID_VERSION_BUILD_VALUES,
        ),
    )


class VersionFromStringTestCase(unittest.TestCase):
    """
        Version.from_string() のテストケース.
    """

    def test_if_valid_version_string_passed(self):
        """
            有効なバージョン文字列を渡すと, パースに成功する.
        """
        test_cases = (
            (Version(1, 2, 3, None, None), "1.2.3"),
            (Version(1, 2, 3, "alpha", None), "1.2.3-alpha"),
            (Version(1, 2, 3, "alpha-1", None), "1.2.3-alpha-1"),
            (Version(1, 2, 3, None, "build-777"), "1.2.3+build-777"),
            (Version(1, 2, 3, "alpha", "build-777"), "1.2.3-alpha+build-777"),
            (Version(1, 2, 3, "alpha-1", "build-777"), "1.2.3-alpha-1+build-777"),
        )
        for expected, version_string in test_cases:
            with self.subTest(expected=expected, version_string=version_string):
                actual = Version.from_string(version_string)
                self.assertEqual(expected, actual)

    def test_if_invalid_version_string_passed(self):
        """
            無効なバージョン文字列を渡すと, VersionError が発生する.
        """
        test_cases = (
            "1",
            "1.2",
            "\n1.2.3",
            "1.2.3\n",
            "1.2.3.4",
            "1.2.3-",
            "1.2.3+",
            "1.2.3-alpha+",
            "1.2.3-alpha+build+777",
        )
        for version_string in test_cases:
            with self.subTest(version_string=version_string):
                with self.assertRaises(VersionError):
                    Version.from_string(version_string)


class VersionValidateVersionTestCase(unittest.TestCase):
    """
        Version._validate_version() のテストケース.
    """

    def test_if_valid_version_passed(self):
        """
            有効なバージョンを渡す場合.
        """
        for version_tuple in _valid_versions():
            with self.subTest(version_tuple=version_tuple):
                Version._validate_version(*version_tuple)

    def test_if_invalid_version_passed(self):
        """
            無効なバージョンを渡す場合.
        """
        for version_tuple in _invalid_versions():
            with self.subTest(version_tuple=version_tuple):
                with self.assertRaises(VersionError):
                    Version._validate_version(*version_tuple)


class VersionCompareVersionTestCase(unittest.TestCase):
    """
        Version._compare_version() のテストケース.
    """

    def test(self):
        test_cases = (
            # (major, minor, patch, None, None) の場合.
            (0, "1.2.3", "1.2.3"),
            (-1, "1.1.0", "1.1.1"),
            (+1, "1.1.1", "1.1.0"),
            (-1, "1.0.1", "1.1.1"),
            (+1, "1.1.1", "1.0.1"),
            (-1, "0.1.1", "1.1.1"),
            (+1, "1.1.1", "0.1.1"),
            # pre_release を含む場合.
            (0, "1.2.3-alpha", "1.2.3-alpha"),
            (-1, "1.2.3-alpha", "1.2.3"),
            (+1, "1.2.3", "1.2.3-alpha"),
            (-1, "1.2.3-alpha", "1.2.3-alpha.2"),
            (+1, "1.2.3-alpha.2", "1.2.3-alpha"),
            (-1, "1.2.3-alpha", "1.2.3-beta"),
            (+1, "1.2.3-beta", "1.2.3-alpha"),
            # build は無視して比較される.
            (0, "1.2.3+build-1", "1.2.3+build-2"),
            (0, "1.2.3-alpha+build-1", "1.2.3-alpha+build-2"),
        )
        for expected, version_string1, version_string2 in test_cases:
            version1 = Version.from_string(version_string1)
            version2 = Version.from_string(version_string2)
            with self.subTest(expected=expected, version1=version1, version2=version2):
                actual = Version._compare_version(version1, version2)
                self.assertEqual(expected, actual)


class VersionCompareVersionPreReleaseTestCase(unittest.TestCase):
    """
        Version._compare_version_pre_release() のテストケース.
    """

    def test(self):
        test_cases = (
            # 両方が None の場合は 0 となる.
            (0, None, None),
            # 片方が None の場合, None の方が大きいと判断される.
            (-1, "alpha", None),
            (+1, None, "alpha"),
            # 数字のみを含む場合は数値として比較される.
            (0, "123", "123"),
            (-1, "123", "124"),
            (+1, "124", "123"),
            (-1, "1", "10"),
            (+1, "10", "1"),
            # 数値以外を含む場合は辞書順で比較される.
            (0, "alpha", "alpha"),
            (-1, "alpha", "beta"),
            (+1, "beta", "alpha"),
            (0, "1g", "1g"),
            (-1, "10g", "1g"),
            (+1, "1g", "10g"),
            # "." を含む場合は "." で区切った各値を比較する.
            (0, "alpha.1", "alpha.1"),
            (-1, "alpha.1", "alpha.2"),
            (+1, "alpha.2", "alpha.1"),
            (-1, "alpha.1", "alpha.1.1"),
            (+1, "alpha.1.1", "alpha.1"),
        )
        for expected, pre_release1, pre_release2 in test_cases:
            with self.subTest(pre_release1=pre_release1, pre_release2=pre_release2):
                actual = Version._compare_version_pre_release(pre_release1, pre_release2)
                self.assertEqual(expected, actual)


class VersionInitTestCase(unittest.TestCase):
    """
        Version.__init__() のテストケース.
    """

    def test_if_valid_arguments_passed(self):
        """
            有効なバージョンを渡す場合.
        """
        version_tuples = (
            (1, 2, 3, None, None),
            (1, 2, 3, "alpha", None),
            (1, 2, 3, None, "build-777"),
            (1, 2, 3, "alpha", "build-777"),
        )
        for version_tuple in version_tuples:
            with self.subTest(version_tuple=version_tuple):
                version = Version(*version_tuple)
                self.assertEqual(version_tuple[0], version.major)
                self.assertEqual(version_tuple[1], version.minor)
                self.assertEqual(version_tuple[2], version.patch)
                self.assertEqual(version_tuple[3], version.pre_release)
                self.assertEqual(version_tuple[4], version.build)

    def test_if_invalid_arguments_passed(self):
        """
            無効なバージョンを渡す場合.
        """
        for version_tuple in _invalid_versions():
            with self.subTest(version_tuple=version_tuple):
                with self.assertRaises(VersionError):
                    Version(*version_tuple)


class VersionStrTestCase(unittest.TestCase):
    """
        Version.__str__() のテストケース.
    """

    def test(self):
        test_cases = (
            ("1.2.3", (1, 2, 3, None, None)),
            ("1.2.3-alpha", (1, 2, 3, "alpha", None)),
            ("1.2.3+build-777", (1, 2, 3, None, "build-777")),
            ("1.2.3-alpha+build-777", (1, 2, 3, "alpha", "build-777")),
        )
        for expected, version_tuple in test_cases:
            with self.subTest(version_tuple=version_tuple):
                version = Version(*version_tuple)
                self.assertEqual(expected, str(version))


class VersionReprTestCase(unittest.TestCase):
    """
        Version.__repr__() のテストケース.
    """

    def test(self):
        test_cases = (
            ("Version(1, 2, 3, None, None)", (1, 2, 3, None, None)),
            ("Version(1, 2, 3, 'alpha', None)", (1, 2, 3, "alpha", None)),
            ("Version(1, 2, 3, None, 'build-777')", (1, 2, 3, None, "build-777")),
            ("Version(1, 2, 3, 'alpha', 'build-777')", (1, 2, 3, "alpha", "build-777")),
        )
        for expected, version_tuple in test_cases:
            with self.subTest(version_tuple=version_tuple):
                version = Version(*version_tuple)
                self.assertEqual(expected, repr(version))


class VersionHashTestCase(unittest.TestCase):
    """
        Version.__hash__() のテストケース.
    """

    def test_if_version1_eq_version2(self):
        """
            version1 == version2 の場合.
        """
        version1 = Version(1, 2, 3)
        version2 = Version(1, 2, 3)
        self.assertEqual(hash(version1), hash(version2))

    def test_if_version1_ne_version2(self):
        """
            version1 != version2 の場合.

            異なるバージョンでもハッシュ値が衝突する可能性はゼロではない.
            このテストが失敗した場合は, ハッシュ値が偶然衝突した可能性を確認する必要がある.
        """
        version1 = Version(1, 2, 3)
        version2 = Version(1, 2, 4)
        self.assertNotEqual(hash(version1), hash(version2))


class VersionIterTestCase(unittest.TestCase):
    """
        Version.__iter__() のテストケース.
    """

    def test(self):
        version_tuples = (
            (1, 2, 3, None, None),
            (1, 2, 3, "alpha", None),
            (1, 2, 3, None, "build-777"),
            (1, 2, 3, "alpha", "build-777"),
        )
        for version_tuple in version_tuples:
            with self.subTest(version_tuple=version_tuple):
                version = Version(*version_tuple)
                expected = version_tuple
                actual = tuple(version)
                self.assertEqual(expected, actual)


class VersionComparisonOperatorsTestCase(unittest.TestCase):
    """
        Version の比較演算子のテストケース.
    """

    def test_if_version1_eq_version2(self):
        """
            version1 == version2 の場合.
        """
        with self.subTest():
            version1 = Version(1, 2, 3)
            version2 = Version(1, 2, 3)
            self.assertEqual(True, version1 == version2)
            self.assertEqual(False, version1 != version2)
            self.assertEqual(False, version1 < version2)
            self.assertEqual(True, version1 <= version2)
            self.assertEqual(False, version1 > version2)
            self.assertEqual(True, version1 >= version2)

    def test_if_version1_lt_version2(self):
        """
            version1 < version2 の場合.
        """
        with self.subTest():
            version1 = Version(1, 2, 3)
            version2 = Version(1, 2, 4)
            self.assertEqual(False, version1 == version2)
            self.assertEqual(True, version1 != version2)
            self.assertEqual(True, version1 < version2)
            self.assertEqual(True, version1 <= version2)
            self.assertEqual(False, version1 > version2)
            self.assertEqual(False, version1 >= version2)

    def test_if_version1_gt_version2(self):
        """
            version1 > version2 の場合.
        """
        with self.subTest():
            version1 = Version(1, 2, 4)
            version2 = Version(1, 2, 3)
            self.assertEqual(False, version1 == version2)
            self.assertEqual(True, version1 != version2)
            self.assertEqual(False, version1 < version2)
            self.assertEqual(False, version1 <= version2)
            self.assertEqual(True, version1 > version2)
            self.assertEqual(True, version1 >= version2)


class VersionPropertiesTestCase(unittest.TestCase):
    """
        Version の getter/setter のテストケース.
    """

    def test(self):
        version_tuples = (
            (1, 2, 3, None, None),
            (1, 2, 3, "alpha", None),
            (1, 2, 3, None, "build-777"),
            (1, 2, 3, "alpha", "build-777"),
        )
        for version_tuple in version_tuples:
            with self.subTest(version_tuple=version_tuple):
                version = Version(*version_tuple)
                self.assertEqual(version_tuple[0], version.major)
                self.assertEqual(version_tuple[1], version.minor)
                self.assertEqual(version_tuple[2], version.patch)
                self.assertEqual(version_tuple[3], version.pre_release)
                self.assertEqual(version_tuple[4], version.build)


class VersionBumpMajorTestCase(unittest.TestCase):
    """
        Version.bump_major() のテストケース.
    """

    def test(self):
        version = Version(1, 2, 3, "alpha", "build-777")
        test_cases = (
            (Version(2, 0, 0, None, None), dict()),
            (Version(2, 0, 0, "alpha", None), dict(keep_pre_release=True)),
            (Version(2, 0, 0, None, "build-777"), dict(keep_build=True)),
            (Version(2, 0, 0, "alpha", "build-777"), dict(keep_pre_release=True, keep_build=True)),
        )
        for expected, kwargs in test_cases:
            with self.subTest(version=version, kwargs=kwargs):
                actual = version.bump_major(**kwargs)
                self.assertEqual(expected, actual)

    def test_receiver_never_changes(self):
        """
            オブジェクト自体は変更せず, 新しいインスタンスが返される.
        """
        version_tuple = (1, 2, 3, "alpha", "build-777")
        version = Version(*version_tuple)
        new_version = version.bump_major()
        self.assertIsNot(new_version, version)
        self.assertEqual(Version(*version_tuple), version)


class VersionBumpMinorTestCase(unittest.TestCase):
    """
        Version.bump_minor() のテストケース.
    """

    def test(self):
        version = Version(1, 2, 3, "alpha", "build-777")
        test_cases = (
            (Version(1, 3, 0, None, None), dict()),
            (Version(1, 3, 0, "alpha", None), dict(keep_pre_release=True)),
            (Version(1, 3, 0, None, "build-777"), dict(keep_build=True)),
            (Version(1, 3, 0, "alpha", "build-777"), dict(keep_pre_release=True, keep_build=True)),
        )
        for expected, kwargs in test_cases:
            with self.subTest(version=version, kwargs=kwargs):
                actual = version.bump_minor(**kwargs)
                self.assertEqual(expected, actual)

    def test_receiver_never_changes(self):
        """
            オブジェクト自体は変更せず, 新しいインスタンスが返される.
        """
        version_tuple = (1, 2, 3, "alpha", "build-777")
        version = Version(*version_tuple)
        new_version = version.bump_minor()
        self.assertIsNot(new_version, version)
        self.assertEqual(Version(*version_tuple), version)


class VersionBumpPatchTestCase(unittest.TestCase):
    """
        Version.bump_patch() のテストケース.
    """

    def test(self):
        version = Version(1, 2, 3, "alpha", "build-777")
        test_cases = (
            (Version(1, 2, 4, None, None), dict()),
            (Version(1, 2, 4, "alpha", None), dict(keep_pre_release=True)),
            (Version(1, 2, 4, None, "build-777"), dict(keep_build=True)),
            (Version(1, 2, 4, "alpha", "build-777"), dict(keep_pre_release=True, keep_build=True)),
        )
        for expected, kwargs in test_cases:
            with self.subTest(version=version, kwargs=kwargs):
                actual = version.bump_patch(**kwargs)
                self.assertEqual(expected, actual)

    def test_receiver_never_changes(self):
        """
            オブジェクト自体は変更せず, 新しいインスタンスが返される.
        """
        version_tuple = (1, 2, 3, "alpha", "build-777")
        version = Version(*version_tuple)
        new_version = version.bump_patch()
        self.assertIsNot(new_version, version)
        self.assertEqual(Version(*version_tuple), version)


class VersionBumpPreReleaseTestCase(unittest.TestCase):
    """
        Version.bump_pre_release() のテストケース.
    """

    def test_if_valid_pre_release_passed(self):
        """
            有効なプレリリースバージョンを渡す場合.
        """
        version = Version(1, 2, 3, "alpha", "build-777")
        test_cases = (
            (Version(1, 2, 3, None, "build-777"), None),
            (Version(1, 2, 3, "beta", "build-777"), "beta"),
        )
        for expected, pre_release in test_cases:
            with self.subTest(version=version, pre_release=pre_release):
                actual = version.bump_pre_release(pre_release)
                self.assertEqual(expected, actual)

    def test_if_invalid_pre_release_passed(self):
        """
            無効なプレリリースバージョンを渡すと, VersionError が発生する.
        """
        version = Version(1, 2, 3, "alpha", "build-777")
        for pre_release in INVALID_VERSION_PRE_RELEASE_VALUES:
            with self.subTest(version=version, pre_release=pre_release):
                with self.assertRaises(VersionError):
                    version.bump_pre_release(pre_release)


class VersionBumpBuildTestCase(unittest.TestCase):
    """
        Version.bump_build() のテストケース.
    """

    def test_if_valid_version_passed(self):
        """
            有効なバージョンを渡す場合.
        """
        version = Version(1, 2, 3, "alpha", "build-777")
        test_cases = (
            (Version(1, 2, 3, "alpha", None), None),
            (Version(1, 2, 3, "alpha", "build-888"), "build-888"),
        )
        for expected, build in test_cases:
            with self.subTest(version=version, build=build):
                actual = version.bump_build(build)
                self.assertEqual(expected, actual)

    def test_if_invalid_build_passed(self):
        """
            無効なビルドメタデータを渡すと, VersionError が発生する.
        """
        version = Version(1, 2, 3, "alpha", "build-777")
        for build in INVALID_VERSION_BUILD_VALUES:
            with self.subTest(version=version, build=build):
                with self.assertRaises(VersionError):
                    version.bump_build(build)


if __name__ == "__main__":
    unittest.main()

