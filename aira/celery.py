import os
import socket
import textwrap

from django.conf import settings
from django.core.mail import mail_admins

from celery import Celery
from celery.signals import task_failure

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aira_project.settings.local")

app = Celery("aira")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@task_failure.connect()
def email_failed_task(**kwargs):
    if not settings.AIRA_CELERY_SEND_TASK_ERROR_EMAILS:
        return
    subject = "[celery@{host}] {sender.name}: {exception}".format(
        host=socket.gethostname(), **kwargs
    )
    message = textwrap.dedent(
        """\
        Task id: {task_id}

        {einfo}
        """
    ).format(**kwargs)
    mail_admins(subject, message)
