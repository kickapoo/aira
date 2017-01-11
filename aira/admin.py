from django.contrib import admin
from .models import (Agrifield, Profile, IrrigationLog,
                     CropType, IrrigationType, AdviceLog)


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


class IrrigationLogInline(admin.TabularInline):
    model = IrrigationLog
    extra = 1
    ordering = ('-time', )


class AdviceLogInline(admin.TabularInline):
    model = AdviceLog
    extra = 0
    ordering = ('-created_at', )


class AgrifieldAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'is_virtual', 'crop_type',
                    'irrigation_type')
    search_fields = ('owner__username', 'name')
    list_filter = ('is_virtual',)
    ordering = ('name', 'area')

    inlines = [
        IrrigationLogInline,
        AdviceLogInline
    ]


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
admin.site.register(CropType, CropTypeAdmin)
admin.site.register(IrrigationType, IrrigationTypeAdmin)
