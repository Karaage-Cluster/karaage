import logging

from django.contrib import messages
from django.db import transaction

from karaage.common import log
from karaage.plugins.kgapplications import emails
from karaage.plugins.kgapplications.views import base


logger = logging.getLogger(__name__)


class TransitionOpen(base.Transition):
    """A transition after application opened."""

    actions = {"success"}

    def get_next_action(self, request, application, roles):
        """Retrieve the next state."""
        application.reopen()
        link, is_secret = base.get_email_link(application)
        emails.send_invite_email(application, link, is_secret)
        messages.success(request, "Sent an invitation to %s." % application.applicant.email)
        return "success"


class TransitionSubmit(base.Transition):
    """A transition after application submitted."""

    actions = {"success", "error"}

    def get_next_action(self, request, application, roles):
        """Retrieve the next state."""

        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check_valid()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return "error"

        # mark as submitted
        application.submit()

        return "success"


class TransitionApprove(base.Transition):
    """A transition after application fully approved."""

    actions = {"password_needed", "password_ok", "error"}

    def get_next_action(self, request, application, roles):
        """Retrieve the next state."""
        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check_valid()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return "error"

        application.extend()

        # approve application
        try:
            approved_by = request.user
            with transaction.atomic():
                created_person, created_account = application.approve(approved_by)
        except Exception as e:
            logger.exception("Error approving application")
            log.comment(application.application_ptr, f"Error approving application: {e}")
            messages.error(request, e)
            return "error"
        else:
            # send email
            link, is_secret = base.get_email_link(application)
            emails.send_approved_email(application, created_person, created_account, link, is_secret)

            if created_person or created_account:
                return "password_needed"
            else:
                return "password_ok"


class TransitionSplit(base.Transition):
    """A transition after application submitted."""

    actions = {"existing_project", "new_project", "error"}

    def get_next_action(self, request, application, roles):
        """Retrieve the next state."""
        # Do we need to wait for leader or delegate approval?
        if application.project is None:
            return "new_project"
        else:
            return "existing_project"
