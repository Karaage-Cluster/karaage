"""
filters.py - misc stuff for handling LDAP filter strings (see RFC2254)

"""
import six


def escape_filter_chars(assertion_value, escape_mode=0):
    """
    Replace all special characters found in assertion_value
    by quoted notation.

    escape_mode
        If 0 only special chars mentioned in RFC 4515 are escaped.
        If 1 all NON-ASCII chars are escaped.
        If 2 all chars are escaped.
    """

    if isinstance(assertion_value, six.text_type):
        assertion_value = assertion_value.encode("utf_8")

    s = []
    for c in assertion_value:
        do_escape = False

        if str != bytes:  # Python 3
            pass
        else:  # Python 2
            c = ord(c)

        if escape_mode == 0:
            if c == ord('\\') or c == ord('*') \
                    or c == ord('(') or c == ord(')') \
                    or c == ord('\x00'):
                do_escape = True
        elif escape_mode == 1:
            if c < '0' or c > 'z' or c in "\\*()":
                do_escape = True
        elif escape_mode == 2:
            do_escape = True
        else:
            raise ValueError('escape_mode must be 0, 1 or 2.')

        if do_escape:
            s.append(b"\\%02x" % c)
        else:
            b = None
            if str != bytes:  # Python 3
                b = bytes([c])
            else:  # Python 2
                b = chr(c)
            s.append(b)

    return b''.join(s)


def filter_format(filter_template, assertion_values):
    """
    filter_template
          String containing %s as placeholder for assertion values.
    assertion_values
          List or tuple of assertion values. Length must match
          count of %s in filter_template.
    """
    assert isinstance(filter_template, bytes)
    return filter_template % (
        tuple(map(escape_filter_chars, assertion_values)))
