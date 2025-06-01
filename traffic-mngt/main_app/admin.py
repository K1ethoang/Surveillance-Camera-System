from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Accident, AccidentDetail


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )

    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)


class AccidentDetailInline(admin.TabularInline):
    model = AccidentDetail

    fields = ('label', 'confidence', 'bbox')
    extra = 0  # Không hiện dòng trống thêm mặc định

class AccidentDetailAdmin(admin.ModelAdmin):
    model = AccidentDetail

    list_display = ('accident', 'label', 'confidence', 'bbox')
    list_filter = ('label',)

    search_fields = ('accident__camera_serial', 'label')
    ordering = ('-created_at',)

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(AccidentDetail, AccidentDetailAdmin)


class AccidentAdmin(admin.ModelAdmin):
    model = Accident

    list_display = ('detected_at', 'camera_serial', 'confidence', 'confirmed_by', 'snapshot_preview',)
    list_filter =  ('camera_serial','confirmed_by',)

    ordering = ("-created_at",)
    readonly_fields = ("detected_at", "confirmed_by", "camera_serial", "confidence", "snapshot_url")
    inlines = [AccidentDetailInline]

    def snapshot_preview(self, obj):
        if obj.snapshot_url:
            return format_html('<img src="{}" width="300" />', obj.snapshot_url)
        return "No Image"

    snapshot_preview.short_description = "Snapshot"

admin.site.register(Accident, AccidentAdmin)



