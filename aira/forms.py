from django import forms
from .models import Agrifield, Profile, IrrigationLog
from django.utils.translation import ugettext_lazy as _


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('farmer',)


class AgrifieldForm(forms.ModelForm):
    class Meta:
        model = Agrifield
        exclude = ('owner',)
        labels = {
            'name': _('Agriculture Field '),
            'lat': _('Latitude (WGS84)'),
            'lon': _('Longitude (WGS84)'),
            'ct': _('Crop Type'),
            'irrt': _('Irrigation Type'),
            'area': _('Field Area (square meters)')
        }


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)
        labels = {
            'time': _('Datatime(Y/M/D h:m:s) '),
            'water_amount': _('Water (cubic meters)'),
        }
