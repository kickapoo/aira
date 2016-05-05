# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from aira.irma.main import FC_FILE as fc_raster
from aira.irma.main import PWP_FILE as pwp_raster
from aira.irma.main import THETA_S_FILE as thetaS_raster
from aira.irma.main import raster2point

# notification_options is the list of options the user can select for
# notifications, e.g. be notified every day, every two days, every week, and so
# on. It is a dictionary; the key is an id of the option, and the value is a
# tuple whose first element is the human-readable description of an option,
# and the second element is a function receiving a single argument (normally
# the current date) and returning True if notifications are due in that
# particular date.

notification_options = OrderedDict((
    ("D", (_("Day"), lambda x: True)),
    ("2D", (_("2 Days"), lambda x: x.toordinal() % 2 == 0)),
    ("3D", (_("3 Days"), lambda x: x.toordinal() % 3 == 0)),
    ("4D", (_("4 Days"), lambda x: x.toordinal() % 4 == 0)),
    ("5D", (_("5 Days"), lambda x: x.toordinal() % 5 == 0)),
    ("7D", (_("Week"), lambda x: x.weekday() == 0)),
    ("10D", (_("10 Day"), lambda x: x.day in (1, 11, 21))),
    ("30D", (_("Month"), lambda x: x.day == 1)),
))


YES_OR_NO = (
    (True, _('Yes')),
    (False, _('No'))
)

YES_OR_NO_OR_NULL = (
    (True, _('Yes')),
    (False, _('No')),
    (None,'-')
)

EMAIL_LANGUAGE_CHOISES = (
     ('en', 'English'),
     ('el', 'Ελληνικά')
)


class Profile(models.Model):
    farmer = models.OneToOneField(User)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    notification = models.CharField(
        max_length=3, blank=True, default='',
        choices=[(x, notification_options[x][0])
                 for x in notification_options])
    email_language = models.CharField(max_length=3,
         default=EMAIL_LANGUAGE_CHOISES[0][0], choices=EMAIL_LANGUAGE_CHOISES)
    supervisor = models.ForeignKey(User, related_name='supervisor', null=True,
                                   blank=True)
    supervision_question = models.BooleanField(choices=YES_OR_NO,
                                               default=False)

    class Meta:
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return u"UserProfile: {}".format(self.farmer)


class CropType(models.Model):
    name = models.CharField(max_length=100)
    root_depth_max = models.FloatField()
    root_depth_min = models.FloatField()
    max_allow_depletion = models.DecimalField(max_digits=6, decimal_places=2)
    kc = models.FloatField()
    fek_category = models.IntegerField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Crop Types'

    def __unicode__(self):
        return unicode(self.name)


class IrrigationType(models.Model):
    name = models.CharField(max_length=100)
    efficiency = models.FloatField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Irrigation Types'

    def __unicode__(self):
        return unicode(self.name)


class Agrifield(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255,
                            default='i.e. MyField1')
    is_virtual = models.NullBooleanField(choices=YES_OR_NO_OR_NULL, null=True,
                                         default=None)
    # Latitude / Longitude are crucial locations parameters
    # Keeping their long names is more clear for developers/users
    latitude = models.FloatField()
    longitude = models.FloatField()
    crop_type = models.ForeignKey(CropType)
    irrigation_type = models.ForeignKey(IrrigationType)
    area = models.FloatField()
    irrigation_optimizer = models.FloatField(default=0.5)
    use_custom_parameters = models.BooleanField(default=False)
    custom_kc = models.FloatField(null=True, blank=True,
                                  validators=[
                                      MaxValueValidator(1.50),
                                      MinValueValidator(0.10)
                                  ])
    custom_root_depth_max = models.FloatField(null=True, blank=True,
                                              validators=[
                                                  MaxValueValidator(4.00),
                                                  MinValueValidator(0.20)
                                              ])
    custom_root_depth_min = models.FloatField(null=True, blank=True,
                                              validators=[
                                                  MaxValueValidator(2.00),
                                                  MinValueValidator(0.1)
                                              ])
    custom_max_allow_depletion = models.FloatField(null=True, blank=True,
                                                   validators=[
                                                       MaxValueValidator(1.00),
                                                       MinValueValidator(0.00)
                                                   ])
    custom_efficiency = models.FloatField(null=True, blank=True,
                                          validators=[
                                              MaxValueValidator(1.00),
                                              MinValueValidator(0.05)
                                          ])
    custom_irrigation_optimizer = models.FloatField(null=True, blank=True,
                                                    validators=[
                                                        MaxValueValidator(
                                                            1.00),
                                                        MinValueValidator(0.10)
                                                    ])
    custom_field_capacity = models.FloatField(null=True, blank=True,
                                              validators=[
                                                  MaxValueValidator(0.45),
                                                  MinValueValidator(0.10)
                                              ])
    custom_thetaS = models.FloatField(null=True, blank=True,
                                      validators=[
                                          MaxValueValidator(0.55),
                                          MinValueValidator(0.30)
                                      ])
    custom_wilting_point = models.FloatField(null=True, blank=True,
                                             validators=[
                                                 MaxValueValidator(0.22),
                                                 MinValueValidator(0.00)
                                             ])

    @property
    def get_wilting_point(self):
        if self.use_custom_parameters:
            if self.custom_wilting_point in [None, '']:
                return raster2point(self.latitude, self.longitude, pwp_raster)
            return self.custom_wilting_point
        else:
            return raster2point(self.latitude, self.longitude, pwp_raster)

    @property
    def get_thetaS(self):
        if self.use_custom_parameters:
            if self.custom_thetaS in [None, '']:
                return raster2point(self.latitude, self.longitude,
                                    thetaS_raster)
            return self.custom_thetaS
        else:
            return raster2point(self.latitude, self.longitude, thetaS_raster)

    @property
    def get_field_capacity(self):
        if self.use_custom_parameters and self.custom_field_capacity:
            return self.custom_field_capacity
        else:
            return raster2point(self.latitude, self.longitude, fc_raster)

    @property
    def get_efficiency(self):
        if self.use_custom_parameters:
            if self.custom_efficiency in [None, '']:
                return self.irrigation_type.efficiency
            return self.custom_efficiency
        else:
            return self.irrigation_type.efficiency

    @property
    def get_mad(self):
        if self.use_custom_parameters:
            if self.custom_max_allow_depletion in [None, '']:
                return self.crop_type.max_allow_depletion
            return self.custom_max_allow_depletion
        else:
            return self.crop_type.max_allow_depletion

    @property
    def get_kc(self):
        if self.use_custom_parameters:
            if self.custom_kc in [None, '']:
                return self.crop_type.kc
            return self.custom_kc
        else:
            return self.crop_type.kc

    @property
    def get_root_depth_max(self):
        if self.use_custom_parameters:
            if self.custom_root_depth_max in [None, '']:
                return self.crop_type.root_depth_max
            return self.custom_root_depth_max
        else:
            return self.crop_type.root_depth_max

    @property
    def get_root_depth_min(self):
        if self.use_custom_parameters:
            if self.custom_root_depth_min in [None, '']:
                return self.crop_type.root_depth_min
            return self.custom_root_depth_min
        else:
            return self.crop_type.root_depth_min

    @property
    def get_irrigation_optimizer(self):
        if self.use_custom_parameters:
            if self.custom_irrigation_optimizer in [None, '']:
                return self.irrigation_optimizer
            return self.custom_irrigation_optimizer
        else:
            return self.irrigation_optimizer

    def can_edit(self, user):
        if (user == self.owner) or (user == self.owner.profile.supervisor):
            return True
        raise Http404

    class Meta:
        ordering = ('name', 'area')
        verbose_name_plural = 'Agrifields'

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        super(Agrifield, self).save(*args, **kwargs)
        self.execute_model()

    def execute_model(self):
        from aira import tasks

        cache_key = 'agrifield_{}_status'.format(self.id)

        # If the agrifield is already in the Celery queue for calculation,
        # return without doing anything.
        if cache.get(cache_key) == 'queued':
            return

        tasks.calculate_agrifield.delay(self)
        cache.set(cache_key, 'queued', None)

    @property
    def status(self):
        return cache.get('agrifield_{}_status'.format(self.id))


class IrrigationLog(models.Model):
    agrifield = models.ForeignKey(Agrifield)
    time = models.DateTimeField()
    applied_water = models.FloatField(null=True, blank=True,
                                      validators=[
                                          MinValueValidator(0.0)
                                      ])

    def can_edit(self, agriobj):
        if agriobj == self.agrifield:
            return True
        raise Http404

    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)
        verbose_name_plural = 'Irrigation Logs'

    def __unicode__(self):
        return unicode(self.time)

    def save(self, *args, **kwargs):
        super(IrrigationLog, self).save(*args, **kwargs)
        self.agrifield.execute_model()

    def delete(self, *args, **kwargs):
        super(IrrigationLog, self).delete(*args, **kwargs)
        self.agrifield.execute_model()
