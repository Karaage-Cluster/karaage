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

""" High level database interaction. """
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)

import ldap3.core
import ldap3.core.exceptions

import tldap.fields
import tldap.query
from tldap import Q
from tldap.backend.base import LdapBase
from tldap.dict import ImmutableDict
from tldap.dn import dn2str, str2dn
from tldap.exceptions import (
    MultipleObjectsReturned,
    ObjectAlreadyExists,
    ObjectDoesNotExist,
    ValidationError,
)


NotLoadedListType = List[Any] or 'NotLoadedList'


class SearchOptions:
    """ Application specific search options. """
    def __init__(self, base_dn: str, object_class: Set[str], pk_field: str) -> None:
        self.base_dn = base_dn
        self.object_class = object_class
        self.pk_field = pk_field


class Database:
    def __init__(self, connection: LdapBase, settings: Optional[dict] = None):
        self._connection = connection
        if settings is None:
            settings = connection.settings_dict
        self._settings = settings

    @property
    def connection(self) -> LdapBase:
        return self._connection

    @property
    def settings(self) -> dict:
        return self._settings


def get_default_database():
    return Database(tldap.backend.connections['default'])


def get_database(database: Optional[Database]) -> Database:
    if database is None:
        return get_default_database()
    else:
        return database


def _python_to_list(value: Any) -> NotLoadedListType:
    if isinstance(value, NotLoadedList):
        return value
    elif isinstance(value, list):
        return value
    elif isinstance(value, set):
        return list(value)
    elif value is None:
        return []
    else:
        return [value]


def _list_to_python(field: tldap.fields.Field, value: NotLoadedListType) -> Any:
    assert not field.is_list
    assert isinstance(value, (list, NotLoadedList))

    if not field.is_list:
        if isinstance(value, NotLoadedList):
            new_value = value
        elif len(value) == 0:
            new_value = None
        elif len(value) == 1:
            new_value = value[0]
        else:
            raise RuntimeError("Non-list value has more then 1 value.")
    else:
        new_value = value
    return new_value


LdapObjectEntity = TypeVar('LdapObjectEntity', bound='LdapObject')
LdapObjectClass = Type['LdapObject']


class LdapObject(ImmutableDict):
    """ A high level python representation of a LDAP object. """

    def __init__(self, d: Optional[dict] = None) -> None:
        self._fields = self.get_fields()
        field_names = set(self._fields.keys())

        python_data: Dict[str, NotLoadedListType] = {
            field_name: []
            for field_name in field_names
        }
        if d is not None:
            python_data.update(d)

        super().__init__(field_names, python_data)

    @classmethod
    def get_fields(cls) -> Dict[str, tldap.fields.Field]:
        raise NotImplementedError()

    @classmethod
    def get_search_options(cls, database: Database) -> SearchOptions:
        raise NotImplementedError()

    @classmethod
    def on_load(cls, python_data: 'LdapObject', database: Database) -> 'LdapObject':
        raise NotImplementedError()

    @classmethod
    def on_save(cls, changes: 'Changeset', database: Database) -> 'Changeset':
        raise NotImplementedError()

    def _set(self, key: str, value: NotLoadedListType) -> None:
        value = _python_to_list(value)
        return super()._set(key, value)

    def __copy__(self: LdapObjectEntity) -> LdapObjectEntity:
        return self.__class__(self._dict)

    # def __getitem__(self, key: str) -> Any:
    #     raise Moew()
    #     value = self._dict[key]
    #     key = self.fix_key(key)
    #     field = self._fields[key]
    #     return _list_to_python(field, value)

    def get_as_single(self, key: str) -> Any:
        value = self._dict[key]
        key = self.fix_key(key)
        field = self._fields[key]
        return _list_to_python(field, value)

    def get_as_list(self, key: str) -> NotLoadedListType:
        return self._dict[key]


ChangesetEntity = TypeVar('ChangesetEntity', bound='Changeset')


Operation = ldap3.MODIFY_ADD or ldap3.MODIFY_REPLACE or ldap3.MODIFY_DELETE


class Changeset(ImmutableDict):
    """ Represents a set of changes to an LdapObject. """

    def __init__(self, fields: Dict[str, tldap.fields.Field], src: LdapObject, d: Optional[dict] = None) -> None:
        self._fields = fields
        self._src = src
        self._changes: Dict[str, List[Tuple[Operation, List[Any]]]] = {}
        self._errors: List[str] = []
        field_names = set(fields.keys())
        super().__init__(field_names, d)

    def __copy__(self: ChangesetEntity) -> ChangesetEntity:
        copy = self.__class__(self._fields, self._src, self._dict)
        copy._changes = self._changes
        return copy

    def get_value_as_single(self, key: str) -> any:
        key = self.fix_key(key)
        if key in self._dict:
            field = self._fields[key]
            return _list_to_python(field, self._dict[key])
        else:
            return self._src.get_as_single(key)

    def get_value_as_list(self, key: str) -> List[Any]:
        if key in self._dict:
            return self._dict[key]
        else:
            return self._src.get_as_list(key)

    @property
    def changes(self) -> Dict[str, List[Tuple[Operation, List[Any]]]]:
        return self._changes

    @staticmethod
    def _python_to_list(value: Any) -> List[Any]:
        value_list = _python_to_list(value)
        if isinstance(value_list, NotLoaded):
            raise RuntimeError("Unexpected NotLoaded value in Changeset.")
        for value in value_list:
            if isinstance(value, NotLoaded):
                raise RuntimeError("Unexpected NotLoaded value in Changeset.")
        return value_list

    def _set(self, key: str, value: Any) -> None:
        old_value = self.get_value_as_list(key)
        value_list = self._python_to_list(value)

        if value_list != old_value:

            operation: Operation = ldap3.MODIFY_REPLACE
            if value is None or value == []:
                operation = ldap3.MODIFY_DELETE

            self._add_mod(key, operation, value_list, overwrite=True)
            self._replay_mod(key, operation, value_list)
        return

    def force_add(self, key: str, value: Any) -> 'Changeset':
        value_list = self._python_to_list(value)
        clone = self.__copy__()
        clone._add_mod(key, ldap3.MODIFY_ADD, value_list)
        clone._replay_mod(key, ldap3.MODIFY_ADD, value_list)
        return clone

    def force_replace(self, key: str, value: Any) -> 'Changeset':
        value_list = self._python_to_list(value)
        clone = self.__copy__()
        clone._add_mod(key, ldap3.MODIFY_REPLACE, value_list)
        clone._replay_mod(key, ldap3.MODIFY_REPLACE, value_list)
        return clone

    def force_delete(self, key: str, value: Any) -> 'Changeset':
        value_list = self._python_to_list(value)
        clone = self.__copy__()
        clone._add_mod(key, ldap3.MODIFY_DELETE, value_list)
        clone._replay_mod(key, ldap3.MODIFY_DELETE, value_list)
        return clone

    def _add_mod(self, key: str, operation: Operation, new_value_list: List[Any], overwrite=False) -> None:
        if any(isinstance(value, list) for value in new_value_list):
            raise RuntimeError("Got list inside a list.")

        key = self.fix_key(key)

        if key in self._changes:
            if overwrite:
                new_list = []
            else:
                new_list = self._changes[key]
        else:
            new_list = []

        new_list = new_list + [(operation, new_value_list)]

        self._changes = {
            **self._changes,
            key: new_list
        }

    def _replay_mod(self, key: str, operation: Operation, new_value_list: List[Any]):
        if any(isinstance(value, list) for value in new_value_list):
            raise RuntimeError("Got list inside a list.")

        key = self.fix_key(key)

        old_value_list = self.get_value_as_list(key)

        if operation == ldap3.MODIFY_ADD:
            assert isinstance(new_value_list, list)
            for value in new_value_list:
                if value not in old_value_list:
                    old_value_list.append(value)
            if len(old_value_list) == 0:
                raise RuntimeError("Can't add 0 items.")

        elif operation == ldap3.MODIFY_REPLACE:
            old_value_list = new_value_list

        elif operation == ldap3.MODIFY_DELETE:
            if len(new_value_list) == 0:
                old_value_list = []
            else:
                for value in new_value_list:
                    old_value_list.remove(value)

        else:
            raise RuntimeError(f"Unknown LDAP operation {operation}.")

        self._dict[key] = old_value_list

        field = self._fields[key]
        try:
            field.validate(old_value_list)
        except tldap.exceptions.ValidationError as e:
            self._errors.append(f"{key}: {e}.")

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    @property
    def errors(self) -> List[str]:
        return self._errors

    @property
    def src(self) -> LdapObject:
        return self._src


class NotLoaded:
    """ Base class to represent a related field that has not been loaded. """

    def __repr__(self):
        raise NotImplementedError()

    def load(self, database: Optional[Database] = None) -> LdapObject or List[LdapObject]:
        raise NotImplementedError()

    @staticmethod
    def _load_one(table: LdapObjectClass, key: str, value: str, database: Optional[Database] = None) -> LdapObject:
        q = Q(**{key: value})
        result = get_one(table, q, database)
        return result

    @staticmethod
    def _load_list(table: LdapObjectClass, key: str, value: str,
                   database: Optional[Database] = None) -> List[LdapObject]:
        q = Q(**{key: value})
        return list(search(table, q, database))


class NotLoadedObject(NotLoaded):
    """ Represents a single object that needs to be loaded. """
    def __init__(self, *, table: LdapObjectClass, key: str, value: str):
        self._table = table
        self._key = key
        self._value = value

    def __repr__(self):
        return f"<NotLoadedObject {self._table} {self._key}={self._value}>"

    def load(self, database: Optional[Database] = None) -> LdapObject:
        return self._load_one(self._table, self._key, self._value, database)


class NotLoadedList(NotLoaded):
    """ Represents a list of objects that needs to be loaded via a single key. """

    def __init__(self, *, table: LdapObjectClass, key: str, value: str):
        self._table = table
        self._key = key
        self._value = value

    def __repr__(self):
        return f"<NotLoadedList {self._table} {self._key}={self._value}>"

    def load(self, database: Optional[Database] = None) -> List[LdapObject]:
        return self._load_list(self._table, self._key, self._value, database)


def changeset(python_data: LdapObject, d: dict) -> Changeset:
    """ Generate changes object for ldap object. """
    table: LdapObjectClass = type(python_data)
    fields = table.get_fields()
    changes = Changeset(fields, src=python_data, d=d)
    return changes


def _db_to_python(db_data: dict, table: LdapObjectClass, dn: str) -> LdapObject:
    """ Convert a DbDate object to a LdapObject. """
    fields = table.get_fields()

    python_data = table({
        name: field.to_python(db_data[name])
        for name, field in fields.items()
        if field.db_field
    })
    python_data = python_data.merge({
        'dn': dn,
    })
    return python_data


def _python_to_mod_new(changes: Changeset) -> Dict[str, List[List[bytes]]]:
    """ Convert a LdapChanges object to a modlist for add operation. """
    table: LdapObjectClass = type(changes.src)
    fields = table.get_fields()

    result: Dict[str, List[List[bytes]]] = {}

    for name, field in fields.items():
        if field.db_field:
            try:
                value = field.to_db(changes.get_value_as_list(name))
                if len(value) > 0:
                    result[name] = value
            except ValidationError as e:
                raise ValidationError(f"{name}: {e}.")

    return result


def _python_to_mod_modify(changes: Changeset) -> Dict[str, List[Tuple[Operation, List[bytes]]]]:
    """ Convert a LdapChanges object to a modlist for a modify operation. """
    table: LdapObjectClass = type(changes.src)
    changes = changes.changes

    result: Dict[str, List[Tuple[Operation, List[bytes]]]] = {}
    for key, l in changes.items():
        field = _get_field_by_name(table, key)

        if field.db_field:
            try:
                new_list = [
                    (operation, field.to_db(value))
                    for operation, value in l
                ]
                result[key] = new_list
            except ValidationError as e:
                raise ValidationError(f"{key}: {e}.")

    return result


def search(table: LdapObjectClass, query: Optional[Q] = None,
           database: Optional[Database] = None, base_dn: Optional[str] = None) -> Iterator[LdapObject]:
    """ Search for a object of given type in the database. """
    fields = table.get_fields()
    db_fields = {
        name: field
        for name, field in fields.items()
        if field.db_field
    }

    database = get_database(database)
    connection = database.connection

    search_options = table.get_search_options(database)

    iterator = tldap.query.search(
        connection=connection,
        query=query,
        fields=db_fields,
        base_dn=base_dn or search_options.base_dn,
        object_classes=search_options.object_class,
        pk=search_options.pk_field,
    )

    for dn, data in iterator:
        python_data = _db_to_python(data, table, dn)
        python_data = table.on_load(python_data, database)
        yield python_data


def get_one(table: LdapObjectClass, query: Optional[Q] = None,
            database: Optional[Database] = None, base_dn: Optional[str] = None) -> LdapObject:
    """ Get exactly one result from the database or fail. """
    results = search(table, query, database, base_dn)

    try:
        result = next(results)
    except StopIteration:
        raise ObjectDoesNotExist(f"Cannot find result for {query}.")

    try:
        next(results)
        raise MultipleObjectsReturned(f"Found multiple results for {query}.")
    except StopIteration:
        pass

    return result


def preload(python_data: LdapObject, database: Optional[Database] = None) -> LdapObject:
    """ Preload all NotLoaded fields in LdapObject. """

    changes = {}

    # Load objects within lists.
    def preload_item(value: Any) -> Any:
        if isinstance(value, NotLoaded):
            return value.load(database)
        else:
            return value

    for name in python_data.keys():
        value_list = python_data.get_as_list(name)

        # Check for errors.
        if isinstance(value_list, NotLoadedObject):
            raise RuntimeError(f"{name}: Unexpected NotLoadedObject outside list.")

        elif isinstance(value_list, NotLoadedList):
            value_list = value_list.load(database)

        else:
            if any(isinstance(v, NotLoadedList) for v in value_list):
                raise RuntimeError(f"{name}: Unexpected NotLoadedList in list.")
            elif any(isinstance(v, NotLoadedObject) for v in value_list):
                value_list = [preload_item(value) for value in value_list]
            else:
                value_list = None

        if value_list is not None:
            changes[name] = value_list

    return python_data.merge(changes)


def insert(python_data: LdapObject, database: Optional[Database] = None) -> LdapObject:
    """ Insert a new python_data object in the database. """
    assert isinstance(python_data, LdapObject)

    table: LdapObjectClass = type(python_data)

    # ADD NEW ENTRY
    empty_data = table()
    changes = changeset(empty_data, python_data.to_dict())

    return save(changes, database)


def save(changes: Changeset, database: Optional[Database] = None) -> LdapObject:
    """ Save all changes in a LdapChanges. """
    assert isinstance(changes, Changeset)

    if not changes.is_valid:
        raise RuntimeError(f"Changeset has errors {changes.errors}.")

    database = get_database(database)
    connection = database.connection

    table = type(changes._src)

    # Run hooks on changes
    changes = table.on_save(changes, database)

    # src dn   | changes dn | result         | action
    # ---------------------------------------|--------
    # None     | None       | error          | error
    # None     | provided   | use changes dn | create
    # provided | None       | use src dn     | modify
    # provided | provided   | error          | error

    src_dn = changes.src.get_as_single('dn')
    if src_dn is None and 'dn' not in changes:
        raise RuntimeError("No DN was given")
    elif src_dn is None and 'dn' in changes:
        dn = changes.get_value_as_single('dn')
        assert dn is not None
        create = True
    elif src_dn is not None and 'dn' not in changes:
        dn = src_dn
        assert dn is not None
        create = False
    else:
        raise RuntimeError("Changes to DN are not supported.")

    assert dn is not None

    if create:
        # Add new entry
        mod_list = _python_to_mod_new(changes)
        try:
            connection.add(dn, mod_list)
        except ldap3.core.exceptions.LDAPEntryAlreadyExistsResult:
            raise ObjectAlreadyExists(
                "Object with dn %r already exists doing add" % dn)
    else:
        mod_list = _python_to_mod_modify(changes)
        if len(mod_list) > 0:
            try:
                connection.modify(dn, mod_list)
            except ldap3.core.exceptions.LDAPNoSuchObjectResult:
                raise ObjectDoesNotExist(
                    "Object with dn %r doesn't already exist doing modify" % dn)

    # get new values
    python_data = table(changes.src.to_dict())
    python_data = python_data.merge(changes.to_dict())
    python_data = python_data.on_load(python_data, database)
    return python_data


def delete(python_data: LdapObject, database: Optional[Database] = None) -> None:
    """ Delete a LdapObject from the database. """
    dn = python_data.get_as_single('dn')
    assert dn is not None

    database = get_database(database)
    connection = database.connection

    connection.delete(dn)


def _get_field_by_name(table: LdapObjectClass, name: str) -> tldap.fields.Field:
    """ Lookup a field by its name. """
    fields = table.get_fields()
    return fields[name]


def rename(python_data: LdapObject, new_base_dn: str = None,
           database: Optional[Database] = None, **kwargs) -> LdapObject:
    """ Move/rename a LdapObject in the database. """
    table = type(python_data)
    dn = python_data.get_as_single('dn')
    assert dn is not None

    database = get_database(database)
    connection = database.connection

    # extract key and value from kwargs
    if len(kwargs) == 1:
        name, value = list(kwargs.items())[0]

        # work out the new rdn of the object
        split_new_rdn = [[(name, value, 1)]]

        field = _get_field_by_name(table, name)
        assert field.db_field

        python_data = python_data.merge({
            name: value,
        })

    elif len(kwargs) == 0:
        split_new_rdn = [str2dn(dn)[0]]
    else:
        assert False

    new_rdn = dn2str(split_new_rdn)

    connection.rename(
        dn,
        new_rdn,
        new_base_dn,
    )

    if new_base_dn is not None:
        split_base_dn = str2dn(new_base_dn)
    else:
        split_base_dn = str2dn(dn)[1:]

    tmp_list = [split_new_rdn[0]]
    tmp_list.extend(split_base_dn)

    new_dn = dn2str(tmp_list)

    python_data = python_data.merge({
        'dn': new_dn,
    })
    return python_data
