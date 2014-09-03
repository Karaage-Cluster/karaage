Customizing Karaage
===================
Karaage can be customized for local requirements. Traditionally this was done
using undocumented methods that were fragile and prone to breakage on upgrades.

This document attempts to document a standard set of methods which will not
break through upgrades, or if breakage is required the procedure to fix the
problem will be documented as part of the upgrade procedure.

Configuration settings
----------------------
There are many settings in ``/etc/karaage3/settings.py`` that can be customized.
See the comments in this file for more information.

..  py:data:: PLUGINS

    A list of classes that define Karaage plugins. For more information on
    creating plugins from scratch, please see the Karaage programmers
    documentation.
