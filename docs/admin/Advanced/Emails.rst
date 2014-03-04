Karaage Emails
==============

Karaage uses a template system to generate emails it sends out to users.

When installing Karaage you will need to rename the example template and
then edit.

All email templates are stored in /etc/karaage/templates/emails just
rename the example from XXXX.example to XXXX

All emails have the following context variables you can use:

-  {{ org\_email }} - settings.ACCOUNTS\_EMAIL,
-  {{ org\_name }} - settings.ACCOUNTS\_ORG\_NAME,

join\_project\_request\_body.txt
--------------------------------

Sent to all project leaders when someone requests to join their project.

Context: \* {{ requestor }} - Name of the person requesting to join the
project \* {{ receiver }} - Name of the person receiving the email \* {{
project }} - Name of the project \* {{ site }} - Link to the site to
approve the application. NOTE this does not include the hostname and web
server prefix. Example /applications/2/

account\_approved\_body.txt
---------------------------

Sent to a user once their account (or request to join a project) is
approved.

Context: \* {{ receiver }} - Name of the person receiving the email \*
{{ project }} - Name of the project \* {{ site }} - Link to the site to
view user profile eg. /profile/

user\_invite\_body.txt
----------------------

Sent to a user who has been invited to join a project.

Context: \* {{ sender }} - Name of the person who invited the user \* {{
project }} - Name of the project \* {{ site }} - Link to the site for
the receiver to go to fill in their application. eg.
/applications/4k4i4kio4kiok4okrt93/ \* {{ make\_leader }} - Boolean to
indicate whether the sender has requested they become a project leader
too. (Use like {% if make\_leader %}Something{% endif %} \* {{ message
}} - Custom message displayed to user from invite form.

email\_footer.txt
-----------------

Text that is displayed at the bottom of each email
