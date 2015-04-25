from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from aira.irma.utils import FC_FILE as fc_raster
from aira.irma.utils import PWP_FILE as pwp_raster
from aira.irma.utils import THETA_S_FILE as thetaS_raster
from aira.irma.utils import raster2point


class Profile(models.Model):
    farmer = models.OneToOneField(User)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return u"UserProfile: {}".format(str(self.farmer))


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
        return u"{}".format(str(self.name))


class IrrigationType(models.Model):
    name = models.CharField(max_length=100)
    efficiency = models.FloatField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Irrigation Types'

    def __unicode__(self):
        return u"{}".format(str(self.name))


class Agrifield(models.Model):
    IRT_LIST = (
        (0.5, 'IRT (50% Inet)'),
        (0.75, 'IRT (75% Inet)'),
        (1.0, 'IRT (100% Inet)'),
    )

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255,
                            default='i.e. MyField1')
    # Latitude / Longitude are crucial locations parameters
    # Keeping their long names is more clear for developers/users
    latitude = models.FloatField()
    longitude = models.FloatField()
    crop_type = models.ForeignKey(CropType)
    irrigation_type = models.ForeignKey(IrrigationType)
    area = models.FloatField()
    irrigation_optimizer = models.FloatField(choices=IRT_LIST,
                                             default=1.0)
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
                                      MaxValueValidator(2.00),
                                      MinValueValidator(0.50)
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
        if self.use_custom_parameters:
            if self.custom_field_capacity in [None, '']:
                return raster2point(self.latitude, self.longitude, fc_raster)
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

    class Meta:
        ordering = ('name', 'area')
        verbose_name_plural = 'Agrifields'

    def __unicode__(self):
        return "User:{} | Agrifield: {}".format(str(self.owner.username),
                                                str(self.name))


class IrrigationLog(models.Model):
    agrifield = models.ForeignKey(Agrifield)
    time = models.DateTimeField()
    applied_water = models.IntegerField(null=True, blank=True)

    class Meta:
        get_latest_by = 'time'
        ordering = ('time',)
        verbose_name_plural = 'Irrigation Logs'

    def __unicode__(self):
        return u"Argifield: {} | TimeLog: {}".format(str(self.agrifield.name),
                                                     str(self.time))
