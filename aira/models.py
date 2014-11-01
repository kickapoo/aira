from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    farmer = models.ForeignKey(User)
    first_name = models.CharField(max_length=255, default="First Name")
    last_name = models.CharField(max_length=255, default="Last Name")
    address = models.CharField(max_length=255,
                               default="Street/ZipCode/State", blank=True)

    class Meta:
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return self.last_name


class CropType(models.Model):
    name = models.CharField(max_length=100)
    crop_coefficient = models.DecimalField(max_digits=6, decimal_places=2)
    root_depth = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'crop Types'

    def __unicode__(self):
        return self.name


class IrrigationType(models.Model):
    name = models.CharField(max_length=100)
    efficiency = models.DecimalField(max_digits=2, decimal_places=2)

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'irrigation Types'

    def __unicode__(self):
        return self.name


class Agrifield(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255,
                            default='i.e. Home Garden')
    cadastre = models.IntegerField(blank=True, null=True)
    lon = models.FloatField()
    lat = models.FloatField()

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'agrifields'

    def __unicode__(self):
        return self.name


class Crop(models.Model):
    agrifield = models.ForeignKey(Agrifield)
    crop_type = models.ForeignKey(CropType)
    irrigation_type = models.ForeignKey(IrrigationType)
    # Area in square meters
    area = models.FloatField()

    class Meta:
        ordering = ('-area',)
        verbose_name_plural = 'crops'

    def __unicode__(self):
        return "{}-{}-{}".format(self.agrifield, self.crop_type,
                                 self.irrigation_type)


class IrrigationLog(models.Model):
    agrifield_crop = models.ForeignKey(Crop)
    time = models.DateTimeField(blank=True, null=True)
    water_amount = models.IntegerField(blank=True, null=True)

    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)
        verbose_name_plural = 'irrigation Logs'

    def __unicode__(self):
        return str(self.time)
