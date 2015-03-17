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
