from collections import OrderedDict
from django.utils.translation import gettext as _

from .misc import ChoiceEnum


NOTIFICATIONS_OPTIONS = OrderedDict((
    ("D", (_("Day"), lambda x: True)),
    ("2D", (_("2 Days"), lambda x: x.toordinal() % 2 == 0)),
    ("3D", (_("3 Days"), lambda x: x.toordinal() % 3 == 0)),
    ("4D", (_("4 Days"), lambda x: x.toordinal() % 4 == 0)),
    ("5D", (_("5 Days"), lambda x: x.toordinal() % 5 == 0)),
    ("7D", (_("Week"), lambda x: x.weekday() == 0)),
    ("10D", (_("10 Day"), lambda x: x.day in (1, 11, 21))),
    ("30D", (_("Month"), lambda x: x.day == 1)),
))


class EMAIL_LANGUAGE_CHOICES(ChoiceEnum):
    EN = _("English")
    EL = _("Ελληνικά")
