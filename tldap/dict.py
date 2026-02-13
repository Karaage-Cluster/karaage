# Copyright 2018 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.
""" Dictionary related classes. """
from typing import Dict, ItemsView, KeysView, Optional, Set, TypeVar


Entity = TypeVar('Entity', bound='CaseInsensitiveDict')


class CaseInsensitiveDict:
    """
    Case insensitve dictionary for searches however preserves the case for
    retrieval. Needs to be supplied with a set of allowed keys.
    """

    def __init__(self, allowed_keys: Set[str], d: Optional[dict] = None) -> None:
        self._lc: Dict[str, str] = {
            value.lower(): value for value in allowed_keys
        }
        self._dict = dict()
        if d is not None:
            for k, v in d.items():
                self[k] = v

    def fix_key(self, key: str) -> str:
        key = key.lower()

        if key not in self._lc:
            raise KeyError(key)

        return self._lc[key.lower()]

    def __setitem__(self, key: str, value: any):
        key = self.fix_key(key)
        self._dict.__setitem__(key, value)

    def __delitem__(self, key: str):
        key = self.fix_key(key)
        del self._lc[key]
        self._dict.__delitem__(key)

    def __getitem__(self, key: str):
        key = self.fix_key(key)
        return self._dict.__getitem__(key)

    def __contains__(self, key: str):
        key = self.fix_key(key)
        return self._dict.__contains__(key)

    def get(self, key: str, default: any = None):
        key = self.fix_key(key)
        return self._dict.get(key, default)

    def keys(self) -> KeysView[str]:
        return self._dict.keys()

    def items(self) -> ItemsView[str, any]:
        return self._dict.items()

    def to_dict(self) -> dict:
        return self._dict


ImmutableDictEntity = TypeVar('ImmutableDictEntity', bound='ImmutableDict')


class ImmutableDict:
    """
    Immutable dictionary that cannot be changed without creating a new instance.
    """
    def __init__(self, allowed_keys: Optional[Set[str]] = None, d: Optional[dict] = None) -> None:
        self._allowed_keys = allowed_keys
        self._dict = CaseInsensitiveDict(allowed_keys)
        if d is not None:
            for key, value in d.items():
                self._set(key, value)

    def fix_key(self, key: str) -> str:
        return self._dict.fix_key(key)

    def __getitem__(self, key: str):
        return self._dict.__getitem__(key)

    def get(self, key: str, default: any = None):
        key = self.fix_key(key)
        try:
            return self._dict.get(key, default)
        except KeyError:
            return default

    def __contains__(self, key: str):
        return self._dict.__contains__(key)

    def keys(self) -> KeysView[str]:
        return self._dict.keys()

    def items(self) -> ItemsView[str, any]:
        return self._dict.items()

    def __copy__(self: ImmutableDictEntity) -> ImmutableDictEntity:
        return self.__class__(self._allowed_keys, self._dict)

    def _set(self, key: str, value: any) -> None:
        self._dict[key] = value

    def merge(self: ImmutableDictEntity, d: dict) -> ImmutableDictEntity:
        clone = self.__copy__()
        for key, value in d.items():
            clone._set(key, value)
        return clone

    def set(self: ImmutableDictEntity, key: str, value: any) -> ImmutableDictEntity:
        clone = self.__copy__()
        clone._set(key, value)
        return clone

    def to_dict(self) -> dict:
        return self._dict.to_dict()
