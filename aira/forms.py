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
        fields = ['name', 'area', 'longitude', 'latitude', 'ct', 'irrt']
        labels = {
            'name': _('Field Name '),
            'latitude': _('Latitude (WGS84)'),
            'longitude': _('Longitude (WGS84)'),
            'ct': _('Crop Type'),
            'irrt': _('Irrigation Type'),
            'area': _('Irrigated Field Area (m<sup>2</sup>)')
        }


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)
        labels = {
            'time': _('Datetime(Y-M-D h:m:s) '),
            'water_amount': _('Water (cubic meters)'),
        }
