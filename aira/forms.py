from django import forms
from .models import Agrifield, Profile, IrrigationLog
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField
from registration.forms import RegistrationForm
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(queryset=User.objects.filter(profile__supervision_question=True),
                                        required=False)

    class Meta:
        model = Profile
        exclude = ('farmer',)

        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'address': _('Address'),
            'notification': _('Email Alert per'),
            'supervisor': _('IRMA Supervisors'),
            'supervision_question': _('Consider me as supervisor')
        }


class AgrifieldForm(forms.ModelForm):
    class Meta:
        model = Agrifield
        exclude = ('owner',)
        fields = ['name', 'area', 'longitude', 'latitude', 'crop_type',
                  'irrigation_type', 'irrigation_optimizer',
                  'use_custom_parameters', 'custom_irrigation_optimizer',
                  'custom_kc',
                  'custom_root_depth_max', 'custom_root_depth_min',
                  'custom_max_allow_depletion', 'custom_efficiency',
                  'custom_field_capacity',
                  'custom_thetaS',
                  'custom_wilting_point']

        labels = {
            'name': _('Field Name'),
            'latitude': _('Latitude (WGS84)'),
            'longitude': _('Longitude (WGS84)'),
            'crop_type': _('Crop Type'),
            'irrigation_type': _('Irrigation Type'),
            'area': _('Irrigated Field Area (m<sup>2</sup>)'),
            'irrigation_optimizer': _("Irrigation Optimizer"),
            'use_custom_parameters': _("Use Custom Parameters"),
            'custom_irrigation_optimizer': _("Irrigation Optimizer"),
            'custom_kc': _("Kc"),
            'custom_root_depth_max': _("Estimated root depth (max)"),
            'custom_root_depth_min': _("Estimated root depth (min)"),
            'custom_max_allow_depletion': _("Maximum Allowable Depletion"),
            'custom_efficiency': _("Irrigation efficiency"),
            'custom_field_capacity': _("Field Capacity"),
            'custom_thetaS': _("Soil moisture at saturation"),
            'custom_wilting_point': _("Permanent Wilting Point")
        }


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)
        labels = {
            'time': _('Datetime (Y-M-D h:m:s) '),
            'applied_water': _('Applied Irrigation Water'),
        }


class MyRegistrationForm(RegistrationForm):
    """
    Extension of the default registration form to include a captcha
    """
    captcha = CaptchaField(label=_('Are you human?'))
