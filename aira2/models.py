from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import gettext as _


from .choices import EMAIL_LANGUAGE_CHOICES, NOTIFICATIONS_OPTIONS
from .misc import CountryField


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    address = models.CharField(
        _("Address"),
        max_length=255,
        blank=True
    )
    zip_code = models.CharField(_("Zip Code"), max_length=12)
    city = models.CharField(_("City"), max_length=1024,)
    country = CountryField()

    notification = models.CharField(
        max_length=3, blank=True, default='',
        choices=[(x, NOTIFICATIONS_OPTIONS[x][0])
                 for x in NOTIFICATIONS_OPTIONS],
    )
    email_language = models.CharField(
        max_length=100,
        default=EMAIL_LANGUAGE_CHOICES.EN,
        choices=EMAIL_LANGUAGE_CHOICES.choices(),
    )
    supervisor = models.ForeignKey(
        User,
        related_name='supervisor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    supervision_question = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Profiles"

    def get_supervised(self):
        "Get users profiles that have set current user (farmer) as supervisor"
        return Profile.objects.filter(supervisor=self.user)

    def __str__(self):
        return "UserProfile: {}".format(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
