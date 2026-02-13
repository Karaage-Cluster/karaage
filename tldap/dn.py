"""
dn.py - misc stuff for handling distinguished names (see RFC 4514)
"""
import six

import tldap.exceptions


def escape_dn_chars(s):
    """
    Escape all DN special characters found in s
    with a back-slash (see RFC 4514, section 2.4)
    """
    if s:
        assert isinstance(s, six.string_types)
        s = s.replace('\\', '\\\\')
        s = s.replace(',', '\\,')
        s = s.replace('+', '\\+')
        s = s.replace('"', '\\"')
        s = s.replace('<', '\\<')
        s = s.replace('>', '\\>')
        s = s.replace(';', '\\;')
        s = s.replace('=', '\\=')
        s = s.replace('\000', '\\\000')
        if s[0] == '#' or s[0] == ' ':
            s = ''.join(('\\', s))
        if s[-1] == ' ':
            s = ''.join((s[:-1], '\\ '))
    return s


def _whitespace(value, i):
    while True:
        if i >= len(value):
            break
        if not _isSPACE(value[i]):
            break
        i = i + 1

    return ("", i)


# --- RFC4512: SINGLE CHARACTERS ---

def _isALPHA(char):
    assert len(char) == 1
    return (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')


def _isleadkeychar(char):
    assert len(char) == 1
    return _isALPHA(char)


def _iskeychar(char):
    assert len(char) == 1
    return _isALPHA(char) or _isDIGIT(char) or char == "-"


def _isDIGIT(char):
    assert len(char) == 1
    return char >= '0' and char <= '9'


def _isHEX(char):
    assert len(char) == 1
    return (char >= '0' and char <= '9') \
        or (char >= 'A' and char <= 'F') \
        or (char >= 'a' and char <= 'f')


def _isSPACE(char):
    assert len(char) == 1
    return char == ' '


def _isDQUOTE(char):
    assert len(char) == 1
    return char == '"'


def _isSHARP(char):
    assert len(char) == 1
    return char == '#'


def _isPLUS(char):
    assert len(char) == 1
    return char == '+'


def _isCOMMA(char):
    assert len(char) == 1
    return char == ','


def _isDOT(char):
    assert len(char) == 1
    return char == "."


def _isSEMI(char):
    assert len(char) == 1
    return char == ";"


def _isLANGLE(char):
    assert len(char) == 1
    return char == "<"


def _isEQUALS(char):
    assert len(char) == 1
    return char == "="


def _isRANGLE(char):
    assert len(char) == 1
    return char == ">"


def _isESC(char):
    assert len(char) == 1
    return char == "\\"


# --- RFC4512: STRINGS ---

def _keystring(value, i):
    start = i

    if i >= len(value):
        return (None, start)
    if not _isleadkeychar(value[i]):
        return (None, start)
    i = i + 1

    while i < len(value) and _iskeychar(value[i]):
        i = i + 1

    return (value[start:i], i)


def _number(value, i):
    start = i

    if i >= len(value):
        return (None, start)

    if not _isDIGIT(value[i]):
        return (None, start)

    if value[i] == "0":
        i = i + 1
        return (value[start:i], i)

    while i < len(value) and _isDIGIT(value[i]):
        i = i + 1

    return (value[start:i], i)


def _numericoid(value, i):
    start = i

    while True:
        (number, i) = _number(value, i)
        if number is None:
            return (None, i)

        if i >= len(value):
            return (value[start:i], i)

        if value[i] != ".":
            return (value[start:i], i)
        i = i + 1


def _descr(value, i):
    return _keystring(value, i)


def _UTFMB(value, i):
    if ord(value[i]) >= 0x80:
        return (value[i], i + 1)

    return (None, i)


# --- RFC 4514: CHARACTERS ---

def _isspecial(value):
    return _isescaped(value) or _isSPACE(value) \
        or _isSHARP(value) or _isEQUALS(value)


def _isescaped(value):
    return _isDQUOTE(value) or _isPLUS(value) or _isCOMMA(value) \
        or _isSEMI(value) or _isLANGLE(value) or _isRANGLE(value)


def _isLUTF1(char):
    # 0x20 space not allowed
    # 0x21 ! allowed
    # 0x22 : not allowed
    # 0x23 '#' not allowed
    assert len(char) == 1
    n = ord(char)
    return (n >= 0x01 and n <= 0x1F) \
        or (n == 0x21) \
        or (n >= 0x24 and n <= 0x2A) \
        or (n >= 0x2D and n <= 0x3A) \
        or (n == 0x3D) \
        or (n >= 0x3F and n <= 0x5B) \
        or (n >= 0x5D and n <= 0x7F)


def _isTUTF1(char):
    # 0x20 space not allowed
    # 0x21 ! allowed
    # 0x22 : not allowed
    # 0x23 '#' allowed
    assert len(char) == 1
    n = ord(char)
    return (n >= 0x01 and n <= 0x1F) \
        or (n == 0x21) \
        or (n >= 0x23 and n <= 0x2A) \
        or (n >= 0x2D and n <= 0x3A) \
        or (n == 0x3D) \
        or (n >= 0x3F and n <= 0x5B) \
        or (n >= 0x5D and n <= 0x7F)


def _isSUTF1(char):
    # 0x20 space allowed
    # 0x21 ! allowed
    # 0x22 : not allowed
    # 0x23 '#' allowed
    assert len(char) == 1
    n = ord(char)
    return (n >= 0x01 and n <= 0x21) \
        or (n >= 0x23 and n <= 0x2A) \
        or (n >= 0x2D and n <= 0x3A) \
        or (n == 0x3D) \
        or (n >= 0x3F and n <= 0x5B) \
        or (n >= 0x5D and n <= 0x7F)


# --- RFC 4514: STRINGS ---

def _leadchar(value, i):
    start = i

    if i >= len(value):
        return (None, start)

    if _isLUTF1(value[i]):
        return (value[i], i + 1)

    (utfmb, i) = _UTFMB(value, i)
    if utfmb is not None:
        return (utfmb, i)

    return (None, start)


def _trailchar(value, i):
    start = i

    if i >= len(value):
        return (None, start)

    if _isTUTF1(value[i]):
        return (value[i], i + 1)

    (utfmb, i) = _UTFMB(value, i)
    if utfmb is not None:
        return (utfmb, i)

    return (None, start)


def _stringchar(value, i):
    start = i

    if i >= len(value):
        return (None, start)

    if _isSUTF1(value[i]):
        return (value[i], i + 1)

    (utfmb, i) = _UTFMB(value, i)
    if utfmb is not None:
        return (utfmb, i)

    return (None, start)


def _distinguishedName(value, i):
    start = i
    result = []

    (relativeDistinguishedName, i) = _relativeDistinguishedName(value, i)
    if relativeDistinguishedName is None:
        return (None, start)
    result.append(relativeDistinguishedName)

    while True:
        # whitespace not allowed by RFC4514 before comma, however is allowed
        # for backword compatability.
        _, i = _whitespace(value, i)

        if i >= len(value):
            return (result, i)
        if not _isCOMMA(value[i]):
            return (result, i)
        i = i + 1

        # whitespace not allowed by RFC4514 after comma, however is allowed for
        # backword compatability.
        _, i = _whitespace(value, i)

        (relativeDistinguishedName, i) = _relativeDistinguishedName(value, i)
        if relativeDistinguishedName is None:
            return (None, start)

        result.append(relativeDistinguishedName)


def _relativeDistinguishedName(value, i):
    start = i
    result = []

    (attributeTypeAndValue, i) = _attributeTypeAndValue(value, i)
    if attributeTypeAndValue is None:
        return (None, start)
    result.append(attributeTypeAndValue)

    while True:
        if i >= len(value):
            return (result, i)
        if not _isPLUS(value[i]):
            return (result, i)
        i = i + 1

        (attributeTypeAndValue, i) = _attributeTypeAndValue(value, i)
        if attributeTypeAndValue is None:
            return (None, start)

        result.append(attributeTypeAndValue)


def _attributeTypeAndValue(value, i):
    (attributeType, i) = _attributeType(value, i)
    if attributeType is None:
        return (None, i)

    if not _isEQUALS(value[i]):
        return (None, i)
    i = i + 1

    (attributeValue, i) = _attributeValue(value, i)
    if attributeValue is None:
        return (None, i)

    return ((attributeType, attributeValue, 1), i)


def _attributeType(value, i):
    (descr, i) = _keystring(value, i)
    if descr is not None:
        return (descr, i)

    (numericoid, i) = _numericoid(value, i)
    if numericoid is not None:
        return (numericoid, i)

    return (None, i)


def _attributeValue(value, i):
    start = i

    (string, i) = _string(value, i)
    if string is not None:
        return (string, i)

    (string, i) = _hexstring(value, i)
    if string is not None:
        return (string, i)

    return (None, start)


def _string(value, i):
    start = i
    result = ""

    if i >= len(value):
        return (None, start)

    (leadchar, i) = _leadchar(value, i)
    if leadchar is not None:
        result += leadchar
    else:
        (pair, i) = _pair(value, i)
        if pair is None:
            return (None, start)
        result += pair

    prev_result = None
    trail_i = i

    while i < len(value):
        this_i = i

        (stringchar, i) = _stringchar(value, i)
        if stringchar is not None:
            this_result = stringchar
        else:
            (pair, i) = _pair(value, i)
            if pair is None:
                break
            this_result = pair

        if prev_result is not None:
            result += prev_result
        prev_result = this_result
        trail_i = this_i

    i = trail_i

    if i >= len(value):
        return (None, start)

    (trailchar, i) = _trailchar(value, i)
    if trailchar is not None:
        result += trailchar
    else:
        (pair, i) = _pair(value, i)
        if pair is None:
            return (None, start)
        result += pair

    return (result, i)


def _pair(value, i):
    start = i

    if i >= len(value):
        return (None, start)
    if not _isESC(value[i]):
        return (None, start)
    i = i + 1

    if i >= len(value):
        return (None, start)
    if _isESC(value[i]) or _isspecial(value[i]):
        return (value[i], i + 1)

    (hexpair, i) = _hexpair(value, i)
    if hexpair is not None:
        return (hexpair, i)

    return (None, start)


def _hexstring(value, i):
    start = i
    result = ""

    if i >= len(value):
        return (None, start)

    if not _isSHARP(value[i]):
        return (None, start)
    i = i + 1

    (hexpair, i) = _hexpair(value, i)
    if hexpair is None:
        return (None, start)
    result += hexpair

    while True:
        (hexpair, i) = _hexpair(value, i)
        if hexpair is None:
            return (result, i)
        result += hexpair


def _hexpair(value, i):
    start = i

    if i >= len(value):
        return (None, start)
    if not _isHEX(value[i]):
        return (None, start)
    i = i + 1

    if i >= len(value):
        return (None, start)
    if not _isHEX(value[i]):
        return (None, start)
    i = i + 1

    return (chr(int(value[start:i], 16)), i)


def str2dn(dn, flags=0):
    """
    This function takes a DN as string as parameter and returns
    a decomposed DN. It's the inverse to dn2str().

    flags describes the format of the dn

    See also the OpenLDAP man-page ldap_str2dn(3)
    """

    # if python2, we need unicode string
    if not isinstance(dn, six.text_type):
        dn = dn.decode("utf_8")

    assert flags == 0
    result, i = _distinguishedName(dn, 0)
    if result is None:
        raise tldap.exceptions.InvalidDN("Cannot parse dn")
    if i != len(dn):
        raise tldap.exceptions.InvalidDN("Cannot parse dn past %s" % dn[i:])
    return result


def dn2str(dn):
    """
    This function takes a decomposed DN as parameter and returns
    a single string. It's the inverse to str2dn() but will always
    return a DN in LDAPv3 format compliant to RFC 4514.
    """
    for rdn in dn:
        for atype, avalue, dummy in rdn:
            assert isinstance(atype, six.string_types)
            assert isinstance(avalue, six.string_types)
            assert dummy == 1

    return ','.join([
        '+'.join([
            '='.join((atype, escape_dn_chars(avalue or '')))
            for atype, avalue, dummy in rdn])
        for rdn in dn
    ])


def explode_dn(dn, notypes=0, flags=0):
    """
    explode_dn(dn [, notypes=0]) -> list

    This function takes a DN and breaks it up into its component parts.
    The notypes parameter is used to specify that only the component's
    attribute values be returned and not the attribute types.
    """
    if not dn:
        return []
    dn_decomp = str2dn(dn, flags)
    rdn_list = []
    for rdn in dn_decomp:
        if notypes:
            rdn_list.append('+'.join([
                escape_dn_chars(avalue or '')
                for atype, avalue, dummy in rdn
            ]))
        else:
            rdn_list.append('+'.join([
                '='.join((atype, escape_dn_chars(avalue or '')))
                for atype, avalue, dummy in rdn
            ]))
    return rdn_list


def explode_rdn(rdn, notypes=0, flags=0):
    """
    explode_rdn(rdn [, notypes=0]) -> list

    This function takes a RDN and breaks it up into its component parts
    if it is a multi-valued RDN.
    The notypes parameter is used to specify that only the component's
    attribute values be returned and not the attribute types.
    """
    if not rdn:
        return []
    rdn_decomp = str2dn(rdn, flags)[0]
    if notypes:
        return [avalue or '' for atype, avalue, dummy in rdn_decomp]
    else:
        return ['='.join((atype, escape_dn_chars(avalue or '')))
                for atype, avalue, dummy in rdn_decomp]
