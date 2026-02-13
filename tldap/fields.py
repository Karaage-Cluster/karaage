# Copyright 2012-2014 Brian May
# -*- coding: UTF-8 -*-

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

""" LDAP field types. """

import datetime
import struct

import six

import tldap.exceptions


class Field(object):
    """ The base field type. """
    db_field = True

    def __init__(self, max_instances=1, required=False):
        self._max_instances = max_instances
        self._required = required

    @property
    def is_list(self):
        return self._max_instances != 1

    def to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """

        # ensure value is valid
        self.validate(value)

        assert isinstance(value, list)
        value = list(value)
        for i, v in enumerate(value):
            value[i] = self.value_to_db(v)

        # return result
        assert isinstance(value, list)
        return value

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        assert isinstance(value, list)

        # convert every value in list
        value = list(value)
        for i, v in enumerate(value):
            value[i] = self.value_to_python(v)

        # return result
        return value

    def validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        # check object type
        if not isinstance(value, list):
            raise tldap.exceptions.ValidationError(
                "is not a list and max_instances is %s" %
                self._max_instances)
        # check maximum instances
        if (self._max_instances is not None and
                len(value) > self._max_instances):
            raise tldap.exceptions.ValidationError(
                "exceeds max_instances of %d" %
                self._max_instances)
        # check this required value is given
        if self._required:
            if len(value) == 0:
                raise tldap.exceptions.ValidationError(
                    "is required")
        # validate the value
        for i, v in enumerate(value):
            self.value_validate(v)

    def clean(self, value):
        """
        Convert the value's type and run validation. Validation errors from
        to_python and validate are propagated. The correct value is returned if
        no error is raised.
        """
        value = self.to_python(value)
        self.validate(value)
        return value

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        raise RuntimeError("Not implemented")

    def value_to_filter(self, value):
        return self.value_to_db(value)

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        raise RuntimeError("Not implemented")

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        raise RuntimeError("Not implemented")


class FakeField(Field):
    db_field = False

    """ Field contains a binary value that can not be interpreted in anyway.
    """
    # def get_db(self, db_data):
    #     return None
    #
    # def set_db(self, db_data, python_value):
    #     pass

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        return None

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        return None

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """


class BinaryField(Field):
    """ Field contains a binary value that can not be interpreted in anyway.
    """

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        assert value is None or isinstance(value, bytes)
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")
        return value

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")


class CharField(Field):
    """ Field contains a UTF8 character string. """

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        if isinstance(value, six.string_types):
            value = value.encode("utf_8")
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")
        value = value.decode("utf_8")
        return value

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not isinstance(value, six.string_types):
            raise tldap.exceptions.ValidationError("should be a string")


class UnicodeField(Field):
    """ Field contains a UTF16 character string. """

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        value = value.encode("utf_16le")
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")
        value = value.decode("utf_16")
        return value

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not isinstance(value, six.string_types):
            raise tldap.exceptions.ValidationError("should be a string")


class IntegerField(Field):
    """ Field contains an integer value. """

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be bytes")
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("is invalid integer")

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        assert isinstance(value, six.integer_types)
        return str(value).encode("utf_8")

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, six.integer_types):
            raise tldap.exceptions.ValidationError("should be a integer")

        try:
            return str(value)
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("is invalid integer")


class DaysSinceEpochField(Field):
    """ Field is an integer containing number of days since epoch. """

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("is invalid integer")

        try:
            value = datetime.date.fromtimestamp(value * 24 * 60 * 60)
        except OverflowError:
            raise tldap.exceptions.ValidationError("is too big a date")

        return value

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        assert isinstance(value, datetime.date)
        assert not isinstance(value, datetime.datetime)

        try:
            value = value - datetime.date(year=1970, month=1, day=1)
        except OverflowError:
            raise tldap.exceptions.ValidationError("is too big a date")

        return str(value.days).encode("utf_8")

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, datetime.date):
            raise tldap.exceptions.ValidationError("is invalid date")
        # a datetime is also a date but they are not compatable
        if isinstance(value, datetime.datetime):
            raise tldap.exceptions.ValidationError("should be a date, not a datetime")


class SecondsSinceEpochField(Field):
    """ Field is an integer containing number of seconds since epoch. """

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("is invalid integer")

        try:
            value = datetime.datetime.utcfromtimestamp(value)
        except OverflowError:
            raise tldap.exceptions.ValidationError("is too big a date")

        return value

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """
        assert isinstance(value, datetime.datetime)

        try:
            value = value - datetime.datetime(1970, 1, 1)
        except OverflowError:
            raise tldap.exceptions.ValidationError("is too big a date")

        value = value.seconds + value.days * 24 * 3600
        value = str(value).encode("utf_8")

        return value

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, datetime.datetime):
            raise tldap.exceptions.ValidationError("is invalid date time")


class SidField(Field):
    """ Field is a binary representation of a Microsoft SID. """

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, bytes):
            raise tldap.exceptions.ValidationError("should be a bytes")

        length = len(value) - 8
        if length % 4 != 0:
            raise tldap.exceptions.ValidationError("Invalid sid")

        length = length // 4

        array = struct.unpack('<bbbbbbbb' + 'I' * length, value)

        if array[1] != length:
            raise tldap.exceptions.ValidationError("Invalid sid")

        if array[2:7] != (0, 0, 0, 0, 0):
            raise tldap.exceptions.ValidationError("Invalid sid")

        array = ("S", ) + array[0:1] + array[7:]
        return "-".join([str(i) for i in array])

    def value_to_db(self, value):
        """ Returns field's single value prepared for saving into a database. """

        assert isinstance(value, str)

        array = value.split("-")
        length = len(array) - 3

        assert length >= 0
        assert array[0] == 'S'

        array = array[1:2] + [length, 0, 0, 0, 0, 0] + array[2:]
        array = [int(i) for i in array]

        return struct.pack('<bbbbbbbb' + 'I' * length, *array)

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type,
        raising django.core.exceptions.ValidationError if the data can't be
        converted.  Returns the converted value. Subclasses should override
        this.
        """
        if not isinstance(value, str):
            raise tldap.exceptions.ValidationError("Invalid sid")

        array = value.split("-")
        length = len(array) - 3

        if length < 1:
            raise tldap.exceptions.ValidationError("Invalid sid")

        if array.pop(0) != "S":
            raise tldap.exceptions.ValidationError("Invalid sid")

        try:
            [int(i) for i in array]
        except TypeError:
            raise tldap.exceptions.ValidationError("Invalid sid")
