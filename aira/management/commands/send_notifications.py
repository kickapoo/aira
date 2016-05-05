from datetime import date, datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from django.contrib.auth.models import User
from aira.models import Profile, Agrifield
from aira.models import notification_options
from aira.irma.main import email_users_response_data, agripoint_in_raster

from django.contrib.sites.models import Site

from django.core.mail import send_mail
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = "Emails irrigation advice notifications to users."

    def handle(self, *args, **options):
        self.template = get_template('aira/email_notification.html')
        for user in User.objects.all():
            if self.send_notification(user):
                if Agrifield.objects.filter(owner=user).exists():
                    user_agrifields = Agrifield.objects.filter(owner=user)
                    self.notify_user(user, user_agrifields, user)
                if Profile.objects.filter(supervisor=user).exists():
                    for supervised_user in Profile.objects.filter(supervisor=user):
                        supervised_user = User.objects.get(username=supervised_user.farmer)
                        if Agrifield.objects.filter(owner=supervised_user).exists():
                            supervised_agrifields = Agrifield.objects.filter(owner=supervised_user)
                            self.notify_user(user, supervised_agrifields, supervised_user)

    def send_notification(self, user):
        if Profile.objects.filter(farmer=user).exclude(notification='').exists():
            user_profile = Profile.objects.get(farmer=user)
            return notification_options[user_profile.notification][1](date.today())
        return False

    def get_email_context(self, agrifields, user, owner ):
        context = Context()
        for f in agrifields:
            f.results = email_users_response_data(f)
        context['owner'] = owner
        context['sd'] = agrifields[0].results.sd
        context['ed'] = agrifields[0].results.ed
        context['agrifields'] = agrifields
        context['site'] = Site.objects.get_current()
        context['user'] = user
        context['timestamp'] = datetime.now()
        return context

    def notify_user(self, user, agrifields, owner):
        # Clear agrifields from the ones outside the study_area
        agrifields = [f for f in agrifields if agripoint_in_raster(f)]
        translation.activate(owner.profile.email_language)
        msg_html = render_to_string('aira/email_notification.html',
                                    self.get_email_context(agrifields, user,
                                                           owner))
        send_mail(_("Irrigation status for ") + str(owner),
                  '',
                  settings.DEFAULT_FROM_EMAIL,
                  [user.email, ],
                  html_message=msg_html)
