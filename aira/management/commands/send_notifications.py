from __future__ import unicode_literals

from datetime import date, datetime
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from aira.irma_utils import agripoint_in_raster, model_results
from aira.models import notification_options, Profile


class Command(BaseCommand):
    help = "Emails irrigation advice notifications to users."

    def handle(self, *args, **options):
        self.template = get_template('aira/email_notification.html')
        for user in User.objects.all():
            if not self.must_send_notification(user):
                continue

            # Send notification for user's own agrifields
            self.notify_user(user, user.agrifield_set.all(), user)

            # If user is a supervisor, send an additional notification to him
            # for each of the supervised users.
            for supervised_user in User.objects.filter(profile__supervisor=user
                                                       ):
                self.notify_user(user, supervised_user.agrifield_set.all(),
                                 supervised_user)

    def must_send_notification(self, user):
        try:
            return notification_options[user.profile.notification][1](
                date.today())
        except (Profile.DoesNotExist, KeyError):
            return False

    def get_email_context(self, agrifields, user, owner):
        context = Context()
        for f in agrifields:
            f.results = model_results(f, "YES")
        if agrifields[0].results is None:
            logging.error(
                ('Internal error: No results for agrifield {} of user {}; '
                 'omitting notification for that user').format(
                     agrifields[0].name, user))
            return None
        context['owner'] = owner
        context['sd'] = agrifields[0].results.sd
        context['ed'] = agrifields[0].results.ed
        context['agrifields'] = agrifields
        context['site'] = Site.objects.get_current()
        context['user'] = user
        context['timestamp'] = datetime.now()
        return context

    def notify_user(self, user, agrifields, owner):
        agrifields = [f for f in agrifields if agripoint_in_raster(f)]
        if not agrifields:
            return
        logging.info('Notifying user {} about the agrifields of user {}'
                     .format(user, owner))
        translation.activate(user.profile.email_language)
        context = self.get_email_context(agrifields, user, owner)
        if context is None:
            return
        msg_html = render_to_string('aira/email_notification.html', context)
        send_mail(_("Irrigation status for ") + unicode(owner),
                  '',
                  settings.DEFAULT_FROM_EMAIL,
                  [user.email, ],
                  html_message=msg_html)
