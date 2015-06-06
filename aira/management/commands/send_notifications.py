from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from aira.models import Profile, notification_options


class Command(BaseCommand):
    help = "Emails irrigation advice notifications to users."

    def handle(self, *args, **options):
        self.template = get_template('aira/email_notification.txt')
        for user in Profile.objects.exclude(notification=''):
            if notification_options[user.notification][1](date.today()):
                self.notify_user(user)

    def notify_user(self, user):
        context = Context({
            'must_irrigate': True,  # FIXME
        })
        send_mail(_("Irrigation status for today"),
                  self.template.render(context),
                  settings.DEFAULT_FROM_EMAIL,
                  [user.farmer.email])
