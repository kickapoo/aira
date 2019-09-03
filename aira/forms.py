from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField
from geowidgets import LatLonField
from registration.forms import RegistrationForm

from .models import Agrifield, IrrigationLog, Profile


class ProfileForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__supervision_question=True), required=False
    )

    class Meta:
        model = Profile
        exclude = ("farmer",)

        labels = {
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "address": _("Address"),
            "notification": _("Email notification per"),
            "email_language": _("Email notification language"),
            "supervisor": _("Supervisor"),
            "supervision_question": _("Consider me as supervisor for other accounts"),
        }


class AgrifieldForm(forms.ModelForm):
    location = LatLonField(
        label=_("Co-ordinates"),
        help_text=_("Longitude and latitude in decimal degrees"),
    )

    class Meta:
        model = Agrifield
        exclude = ("owner",)
        fields = [
            "name",
            "area",
            "location",
            "crop_type",
            "irrigation_type",
            "is_virtual",
            "use_custom_parameters",
            "custom_irrigation_optimizer",
            "custom_root_depth_max",
            "custom_root_depth_min",
            "custom_max_allow_depletion",
            "custom_efficiency",
            "custom_field_capacity",
            "custom_thetaS",
            "custom_wilting_point",
        ]

        labels = {
            "name": _("Field Name"),
            "is_virtual": _("Is this virtual field?"),
            "location": _("Co-ordinates"),
            "crop_type": _("Crop Type"),
            "irrigation_type": _("Irrigation Type"),
            "area": _("Irrigated Field Area (m²)"),
            "use_custom_parameters": _("Use Custom Parameters"),
            "custom_irrigation_optimizer": _("Irrigation Optimizer"),
            "custom_root_depth_max": _("Estimated root depth (max)"),
            "custom_root_depth_min": _("Estimated root depth (min)"),
            "custom_max_allow_depletion": _("Maximum Allowable Depletion"),
            "custom_efficiency": _("Irrigation efficiency"),
            "custom_field_capacity": _("Field Capacity"),
            "custom_thetaS": _("Soil moisture at saturation"),
            "custom_wilting_point": _("Permanent Wilting Point"),
        }

    def clean(self):
        cleaned_data = super(AgrifieldForm, self).clean()
        is_virtual = cleaned_data.get("is_virtual")

        if is_virtual is None:
            msg = _("You must select if field is virtual or not")
            self.add_error("is_virtual", msg)


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ("agrifield",)
        labels = {
            "time": _("Datetime (Y-M-D h:m:s) "),
            "applied_water": _("Applied Irrigation Water"),
        }


class MyRegistrationForm(RegistrationForm):

    """
    Extension of the default registration form to include a captcha
    """

    captcha = CaptchaField(label=_("Are you human?"))
