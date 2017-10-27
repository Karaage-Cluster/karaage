from django.core import management

from celery import shared_task

from karaage.signals import daily_cleanup


@shared_task
def daily():
    management.call_command('lock_expired')
    daily_cleanup.send(sender=daily)
