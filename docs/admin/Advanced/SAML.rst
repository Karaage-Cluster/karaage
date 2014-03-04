SAML/Shibboleth SSO Integration
===============================

*New in Karaage 2.5.5*

How it works
------------

You can enable SAML SSO on a per institute basis by assigning a SAML
entityID to an institute through karaage admin.

The application process has changed, the 1st step asks the user to
select their institute. If the institute has a SAML entityID it will log
the user in via SAML SSO and automatically assign necessary values to a
user (currently first\_name, last\_name, email and institute).

It will add the SAML persistant\_id value to the new user and then this
in future will be able to be used to log the user in. Make sure that the
attribute you use for persistant\_id is unique and persistent.
eduPersonTargetedID is recommended.

If the institute doesn't have a SAM entityID it proceeds as normal and
asks the user for the mentioned attributes.

Required changes
----------------

Required packages
~~~~~~~~~~~~~~~~~

You need to have django-shibboleth installed and have a saml2 endpoint
installed and configured (eg. libapache2-mod-shib2) ### New settings By
default karaage uses the following headers to map to internal values.

::

    SHIB_ATTRIBUTE_MAP = {
        "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
        "HTTP_PERSISTENT_ID": (True, "persistent_id"),
        "HTTP_MAIL": (True, "email"),
        "HTTP_GIVENNAME": (True, "first_name"),
        "HTTP_SN": (True, "last_name"),
        }

If these are different on your system you will need to override the
value. Eg if your header is HTTP\_EMAIL instead of HTTP\_MAIL:

::

    SHIB_ATTRIBUTE_MAP["HTTP_EMAIL"] = (True, "email")

Set Shib handler if yours isn't at the default specified below.

::

    SHIB_HANDLER = '/Shibboleth.sso/DS'

Web server settings
~~~~~~~~~~~~~~~~~~~

You need to protect the following URL with shibboleth lazy auth

/users

NOTE this may be different if you have changed the default web root

Example for shibboleth on apache

::

    <Location "/users">
        AuthType shibboleth
        ShibRequireSession Off
        ShibUseHeaders On
        require shibboleth
    </Location>

