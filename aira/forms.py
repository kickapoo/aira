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
            'lat': _('Latitude (WRS89)'),
        }
        # widgets = {
        #     'name': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        # }


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)
