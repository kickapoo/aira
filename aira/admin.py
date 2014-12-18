from django.contrib import admin
from .models import (Agrifield, Profile, IrrigationLog,
                     CropType, IrrigationType)


class ProfileAdmin(admin.ModelAdmin):
    exclude = ('farmer',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.farmer = request.user
        obj.save()


class AgrifieldAdmin(admin.ModelAdmin):
    pass


class IrrigationLogAdmin(admin.ModelAdmin):
    pass


class CropTypeAdmin(admin.ModelAdmin):
    pass


class IrrigationTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Agrifield, AgrifieldAdmin)
admin.site.register(IrrigationLog, IrrigationLogAdmin)
admin.site.register(CropType, CropTypeAdmin)
admin.site.register(IrrigationType, IrrigationTypeAdmin)
