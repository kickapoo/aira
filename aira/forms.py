from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from .models import (Agrifield, Profile, IrrigationLog)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('farmer',)


class AgrifieldForm(forms.ModelForm):
    class Meta:
        model = Agrifield
        exclude = ('owner',)


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ('agrifield',)

IrrigationLogFormset = inlineformset_factory(Agrifield, IrrigationLog,
                                             can_delete=True, extra=1,
                                             form=IrrigationlogForm)

AgriFieldFormset = inlineformset_factory(User, Agrifield, can_delete=True,
                                         extra=1, form=AgrifieldForm)
