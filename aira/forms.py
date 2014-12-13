from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from .models import (Agrifield, Crop,
                     Profile, IrrigationLog)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('farmer',)


class AgrifieldForm(forms.ModelForm):
    class Meta:
        model = Agrifield
        exclude = ('owner',)


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        exclude = ('agrifield',)


class IrrigationlogForm(forms.ModelForm):
    class Meta:
        model = IrrigationLog
        exclude = ['farmer', 'farmer_field', 'field_crop']

IrrigationLogFormset = inlineformset_factory(Crop, IrrigationLog,
                                             can_delete=True, extra=1,
                                             form=IrrigationlogForm)

AgriFieldFormset = inlineformset_factory(User, Agrifield, can_delete=True,
                                         extra=1, form=AgrifieldForm)
CropFormset = inlineformset_factory(Agrifield, Crop, can_delete=True,
                                    extra=1, form=CropForm)
