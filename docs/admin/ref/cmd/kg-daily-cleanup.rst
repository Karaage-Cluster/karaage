kg-daily-cleanup
================
This utility script should be run daily to clean up certain karaage data.

Description
-----------

Running this command is the same as running the following commands by hand:

.. code-block:: bash

   kg-manage clearsessions
   kg-manage lock_expired
   kg-manage clear_usage_cache
   kg-manage clear_usage_graphs
   kg-manage application_cleanup
   kg-manage link_software --all

For more information, see :doc:`kg-manage`.
