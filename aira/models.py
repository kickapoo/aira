from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    farmer = models.ForeignKey(User)
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
    area = models.FloatField(null=True, blank=True)
    irrigation_optimizer = models.FloatField(choices=IRT_LIST,
                                             default=1.0)
    use_custom_parameters = models.BooleanField(default=False)
    custom_kc = models.FloatField(null=True, blank=True)
    custom_root_depth_max = models.FloatField(null=True, blank=True)
    custom_root_depth_min = models.FloatField(null=True, blank=True)
    custom_max_allow_depletion = models.DecimalField(max_digits=6,
                                                     decimal_places=2,
                                                     null=True, blank=True)
    custom_efficiency = models.FloatField(null=True, blank=True)
    custom_irrigation_optimizer = models.FloatField(null=True, blank=True)

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
    applied_water = models.IntegerField()

    class Meta:
        get_latest_by = 'time'
        ordering = ('time',)
        verbose_name_plural = 'Irrigation Logs'

    def __unicode__(self):
        return u"Argifield: {} | TimeLog: {}".format(str(self.agrifield.name),
                                                     str(self.time))
