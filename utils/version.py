from typing import List, Union, overload


class Version:
    major: int
    minor: int
    patch: int

    def __init__(self, version: str):
        if not isinstance(version, str):
            raise ValueError

        parts = version.split(".")
        self.major = int(parts[0])
        self.minor = int(parts[1])
        self.patch = int(parts[2])

    def __eq__(self, other: Union["Version", str]):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        return self.major == other.major and self.minor == other.minor and self.patch == other.patch

    def __ne__(self, other):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        return not self == other

    def __lt__(self, other):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        if self.major < other.major:
            return True
        if self.minor < other.minor:
            return True
        if self.patch < other.patch:
            return True

    def __gt__(self, other):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        if self.major > other.major:
            return True
        if self.minor > other.minor:
            return True
        if self.patch > other.patch:
            return True

    def __le__(self, other):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        return self < other or self == other

    def __ge__(self, other):
        if not isinstance(other, (Version, str)):
            raise ValueError

        if isinstance(other, str):
            other = Version(other)

        return self > other or self == other

    def to_string(self):
        return f"{self.major}.{self.minor}.{self.patch}"


class VersionsList:
    versions: List[Version]

    @overload
    def __init__(self, versions: List[Version]) -> None:
        for version in versions:
            if not isinstance(version, Version):
                raise ValueError
        self.versions = versions

    @overload
    def __init__(self, *versions: Version) -> None:
        for version in versions:
            if not isinstance(version, Version):
                raise ValueError
        self.versions = versions

    def __contains__(self, item: Version) -> bool:
        return item in self.versions
