from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from .models import Agrifield, Crop, Profile


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
        exclude = ('field',)

AgriFieldFormset = inlineformset_factory(User, Agrifield, can_delete=True,
                                         extra=1, form=AgrifieldForm)
CropFormset = inlineformset_factory(Agrifield, Crop, can_delete=True,
                                    extra=1, form=CropForm)
