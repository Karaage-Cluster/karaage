# Copyright 2012-2018 Brian May
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

""" Hash and check passwords. """
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=[
        "ldap_sha512_crypt",
        "ldap_salted_sha1",
        "ldap_md5",
        "ldap_sha1",
        "ldap_salted_md5",
        "ldap_des_crypt",
        "ldap_md5_crypt",
    ],
    default="ldap_sha512_crypt",
)


def check_password(password: str, encrypted: str) -> bool:
    """ Check a plaintext password against a hashed password. """
    # some old passwords have {crypt} in lower case, and passlib wants it to be
    # in upper case.
    if encrypted.startswith("{crypt}"):
        encrypted = "{CRYPT}" + encrypted[7:]
    return pwd_context.verify(password, encrypted)


def encode_password(password: str) -> str:
    """ Encode a password. """
    return pwd_context.hash(password)
