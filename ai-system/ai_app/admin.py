from django.contrib import admin

from ai_app.models import CameraStream


# Register your models here.
@admin.register(CameraStream)
class CameraStreamAdmin(admin.ModelAdmin):
    model = CameraStream
    list_display = ('serial', 'stream_url', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('serial',)
    ordering = ('-updated_at',)
