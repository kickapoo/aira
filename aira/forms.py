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
        fields = ['name', 'area', 'longitude', 'latitude', 'crop_type',
                  'irrigation_type', 'irrigation_optimizer',
                  'use_custom_parameters', 'custom_irrigation_optimizer',
                  'custom_kc',
                  'custom_root_depth_max', 'custom_root_depth_min',
                  'custom_max_allow_depletion', 'custom_efficiency']

        labels = {
            'name': _('Field Name '),
            'latitude': _('Latitude (WGS84)'),
            'longitude': _('Longitude (WGS84)'),
            'crop_type': _('Crop Type'),
            'irrigation_type': _('Irrigation Type'),
            'area': _('Irrigated Field Area (m<sup>2</sup>)')
        }


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)
        labels = {
            'time': _('Datetime(Y-M-D h:m:s) '),
            'applied_water': _('Water (cubic meters)'),
        }
