from django.contrib import admin
from .models import Agrifield, Profile, CropType, \
    IrrigationLog, IrrigationType


class ProfileAdmin(admin.ModelAdmin):
    exclude = ('farmer',)
    list_display = ['last_name']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.farmer = request.user
        obj.save()


class AgrifieldAdmin(admin.ModelAdmin):
    exclude = ('owner',)

    # def save_model(self, request, obj, form, change):
    #     if not change:
    #         obj.owner = self.field_profile
    #     obj.save()


class IrrigationLogAdmin(admin.ModelAdmin):
    list_display = ['time']


class CropTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


class IrrigationTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Agrifield, AgrifieldAdmin)
admin.site.register(IrrigationLog, IrrigationLogAdmin)
admin.site.register(CropType, CropTypeAdmin)
admin.site.register(IrrigationType, IrrigationTypeAdmin)
