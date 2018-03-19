from django.contrib import admin
from .models import (Agrifield, Profile, IrrigationLog,
                     CropType, IrrigationType)


class ProfileAdmin(admin.ModelAdmin):
    exclude = ('farmer',)
    list_display = ('farmer', 'first_name', 'last_name', 'notification',
                    'supervisor', 'supervision_question')
    search_fields = ('first_name', 'last_name', 'notification')
    list_filter = ('supervision_question',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.farmer = request.user
        obj.save()


class AgrifieldAdmin(admin.ModelAdmin):
    pass


class IrrigationLogAdmin(admin.ModelAdmin):
    pass


class CropTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fek_category', 'max_allow_depletion', 'kc')
    search_fields = ('name', 'fek_category')
    list_filter = ('fek_category',)


class IrrigationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'efficiency')
    search_fields = ('name', 'efficiency')
    list_filter = ('efficiency',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Agrifield, AgrifieldAdmin)
admin.site.register(IrrigationLog, IrrigationLogAdmin)
admin.site.register(CropType, CropTypeAdmin)
admin.site.register(IrrigationType, IrrigationTypeAdmin)
