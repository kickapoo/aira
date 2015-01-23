from django.db import models
from django.contrib.auth.models import User

# Notes:
#   Essential db.fields.#shortname conversions
#       ct: crop type
#       ct_rd: crop type root depth
#       ct_coeff: depletion coefficient
#       ct_kc: crop type capasity
#       irrt: irrigation type
#       irrt_eff: irrigation type efficiency
#       agrifield: agriculture field


class Profile(models.Model):
    farmer = models.ForeignKey(User)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return "UserProfile: {}".format(self.farmer)


class CropType(models.Model):
    ct_name = models.CharField(max_length=100)
    ct_coeff = models.DecimalField(max_digits=6, decimal_places=2)
    ct_rd = models.FloatField()
    ct_kc = models.FloatField()

    class Meta:
        ordering = ('-ct_name',)
        verbose_name_plural = 'Crop Types'

    def __unicode__(self):
        return "{}".format(self.ct_name)


class IrrigationType(models.Model):
    irrt_name = models.CharField(max_length=100)
    irrt_eff = models.FloatField()

    class Meta:
        ordering = ('-irrt_name',)
        verbose_name_plural = 'Irrigation Types'

    def __unicode__(self):
        return "{}".format(self.irrt_name)


class Agrifield(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255,
                            default='i.e. MyField1')
    # Latitude / Longitude are crucial locations parameters
    # Keeping their long names is more clear for developers/users
    latitude = models.FloatField()
    longitude = models.FloatField()
    ct = models.ForeignKey(CropType)
    irrt = models.ForeignKey(IrrigationType)
    area = models.FloatField()

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'Agrifields'

    def __unicode__(self):
        return "User: {} | Agrifield: {}".format(self.owner.username,
                                                 self.name)


class IrrigationLog(models.Model):
    agrifield = models.ForeignKey(Agrifield)
    time = models.DateTimeField()
    water_amount = models.IntegerField()

    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)
        verbose_name_plural = 'Irrigation Logs'

    def __unicode__(self):
        return "Argifield: {} | TimeLog: {}".format(self.agrifield.name,
                                                    str(self.time))
