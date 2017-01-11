# -*- coding: utf-8 -*-
import six
import json
import django_rq

from collections import OrderedDict
from math import pi, sqrt, pow

from django.db import models
from django.core.serializers import serialize
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from aira.irma_utils import FC_FILE as fc_raster
from aira.irma_utils import PWP_FILE as pwp_raster
from aira.irma_utils import THETA_S_FILE as thetaS_raster
from aira.irma_utils import raster2point, agripoint_in_raster

from aira.irma_utils.model import execute_model


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


class Profile(models.Model):

    YES_OR_NO = (
        (True, _('Yes')),
        (False, _('No'))
    )

    EMAIL_LANGUAGE_CHOISES = (
         ('en', 'English'),
         ('el', 'Ελληνικά')
    )

    farmer = models.OneToOneField(User)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    notification = models.CharField(
                        max_length=3,
                        blank=True,
                        default='',
                        choices=[(x, notification_options[x][0])
                                 for x in notification_options])
    email_language = models.CharField(
                        max_length=3,
                        default=EMAIL_LANGUAGE_CHOISES[0][0],
                        choices=EMAIL_LANGUAGE_CHOISES)
    supervisor = models.ForeignKey(
                        User,
                        related_name='supervisor',
                        null=True,
                        blank=True)
    supervision_question = models.BooleanField(choices=YES_OR_NO,
                                               default=False)

    class Meta:
        verbose_name_plural = "Profiles"

    def get_supervised(self):
        return Profile.objects.filter(supervisor=self.farmer)

    def __unicode__(self):
        return u"UserProfile: {}".format(self.farmer)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(farmer=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


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

    YES_OR_NO_OR_NULL = (
        (True, _('Yes')),
        (False, _('No')),
        (None, '-')
    )

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    is_virtual = models.NullBooleanField(
                            choices=YES_OR_NO_OR_NULL,
                            null=True,
                            default=None)
    # Latitude / Longitude are crucial locations parameters
    # Keeping their long names is more clear for developers/users
    latitude = models.FloatField()
    longitude = models.FloatField()
    crop_type = models.ForeignKey(CropType)
    irrigation_type = models.ForeignKey(IrrigationType)
    area = models.FloatField()
    irrigation_optimizer = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)
    use_custom_parameters = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    custom_kc = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(1.50),
                                        MinValueValidator(0.10)])
    custom_root_depth_max = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(4.00),
                                        MinValueValidator(0.20)])
    custom_root_depth_min = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(2.00),
                                        MinValueValidator(0.1)])
    custom_max_allow_depletion = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(1.00),
                                        MinValueValidator(0.00)])
    custom_efficiency = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(1.00),
                                        MinValueValidator(0.05)])
    custom_irrigation_optimizer = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(1.00),
                                        MinValueValidator(0.10)])
    custom_field_capacity = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(0.45),
                                        MinValueValidator(0.10)])
    custom_thetaS = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(0.55),
                                        MinValueValidator(0.30)])
    custom_wilting_point = models.FloatField(
                            null=True, blank=True,
                            validators=[MaxValueValidator(0.22),
                                        MinValueValidator(0.00)])

    class Meta:
        ordering = ('name', 'area')
        verbose_name_plural = 'Agrifields'

    def _get_parameter_value(self, parameter, raster=None):
        """Get the value of parameter based if custom parameters as True/False
        """
        if not isinstance(parameter, six.string_types):
            raise ValidationError(
                _('Got {}, excepted string').format(str(type(parameter)))
            )

        if self.use_custom_parameters and getattr(self, 'custom_' + parameter):
            return round(getattr(self, 'custom_' + parameter), 2)

        raster_options = ['wilting_point', 'thetaS', 'field_capacity']
        if raster and (parameter in raster_options):
            return round(raster2point(self.latitude,
                                      self.longitude, raster), 2)

        if parameter in ['efficiency']:
            return round(getattr(self.irrigation_type, parameter), 2)

        if parameter in ['max_allow_depletion', 'kc', 'root_depth_max',
                         'root_depth_min', 'root_depth_min']:
            return round(getattr(self.crop_type, parameter), 2)
        else:
            return round(getattr(self, parameter), 2)

    def agroparameters(self):
        """ Get Agrifield parameters"""
        return {
            'wp': self._get_parameter_value('wilting_point', pwp_raster),
            'thetaS': self._get_parameter_value('thetaS', thetaS_raster),
            'fc': self._get_parameter_value('field_capacity', fc_raster),
            'irr_eff': self._get_parameter_value('efficiency'),
            'mad': self._get_parameter_value('max_allow_depletion'),
            'kc': self._get_parameter_value('kc'),
            'root_depth_max': self._get_parameter_value('root_depth_max'),
            'root_depth_min': self._get_parameter_value('root_depth_min'),
            'IRT': self._get_parameter_value('irrigation_optimizer'),
            'rd': (self._get_parameter_value('root_depth_max') +
                   self._get_parameter_value('root_depth_min')) / 2,
            'custom_parms': self.use_custom_parameters
        }

    def db_default_agroparameters(self):
        """ Get Agrifield parameters without custom values, db values"""
        return {
            'wp': round(raster2point(self.latitude,
                                     self.longitude,
                                     pwp_raster), 2),
            'thetaS': round(raster2point(self.latitude,
                                         self.longitude,
                                         thetaS_raster), 2),
            'fc': round(raster2point(self.latitude,
                                     self.longitude,
                                     fc_raster), 2),
            'irr_eff': round(self.irrigation_type.efficiency, 2),
            'mad': round(self.crop_type.max_allow_depletion, 2),
            'kc': round(self.crop_type.kc, 2),
            'rd_max': round(self.crop_type.root_depth_max, 2),
            'rd_min': round(self.crop_type.root_depth_min, 2),
            'IRT': round(self.irrigation_optimizer, 2)
        }

    def has_irrigation(self):
        """If has at least one irrigationlog_set. Affects SWB model runs"""
        if self.irrigationlog_set.exists():
            return True
        return False

    def has_irrigation_in_period(self, sdd, edd):
        """If has at least one irrigationlog_set and that is the common period
          Affects SWB model runs"""
        if self.has_irrigation():
            last_irrigation = self.irrigationlog_set.latest()
            lower_end = (last_irrigation.time.date() < sdd)
            upper_end = (last_irrigation.time.date() > edd)
            if lower_end or upper_end:
                return True
        return False

    def last_irrigation(self):
        if self.has_irrigation():
            return self.irrigationlog_set.latest()
        return None

    def execute_swb(self, INET, save_advice=False):
        results = execute_model(self, INET)
        if save_advice:
            AdviceLog.objects.create(agrifield=self,
                                     advice=json.dumps(results),
                                     inet=INET)
        return results

    def async_execute_swb(self, INET, save_advice=False):
        queue = django_rq.get_queue('execute_model')
        job = queue.enqueue(self.execute_swb, INET, save_advice)
        return job._id

    def get_async_swb_results(self, job_hash_id):
        from rq.job import Job
        redis_conn = django_rq.get_connection('execute_model')
        job = Job.fetch(job_hash_id, connection=redis_conn)

        if job.__dict__['_status'] not in ['finished']:
            return job.__dict__['_status'], None
        return job.__dict__['_status'], job.__dict__['_result']

    def advice_history(self):
        return (len(self.advicelog_set.all()), self.advicelog_set.all())

    def in_raster(self):
        return agripoint_in_raster(self)

    def can_edit(self, user):
        if (user == self.owner) or (user == self.owner.profile.supervisor):
            return True
        raise Http404

    def get_radius(self,):
        return round(sqrt(self.area * pow(pi, -1)))

    def as_json(self):
        return json.dumps({
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'virtual': self.is_virtual,
            'owner': self.owner.username,
            'id': self.pk,
            'radius': self.get_radius()
        })

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Agrifield, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.name)


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
        # self.agrifield.execute_model()

    def delete(self, *args, **kwargs):
        super(IrrigationLog, self).delete(*args, **kwargs)
        # self.agrifield.execute_model()


class AdviceLog(models.Model):
    agrifield = models.ForeignKey(Agrifield)
    inet = models.CharField(max_length=10)
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode("Created:{}|Inet:{}".format(self.created_at, self.inet))
