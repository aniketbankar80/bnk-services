from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import StorageConfiguration, DatabaseConfiguration

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active',
                 'is_staff', 'date_joined', 'last_login')
        export_order = fields

class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    resource_class = UserResource

@admin.register(StorageConfiguration)
class StorageConfigurationAdmin(admin.ModelAdmin):
    list_display = ('storage_type', 'is_active', 'storage_capacity')
    list_filter = ('storage_type', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('storage_type', 'is_active')
        }),
        ('AWS S3 Configuration', {
            'classes': ('collapse',),
            'fields': ('aws_access_key_id', 'aws_secret_access_key', 'aws_storage_bucket_name', 'aws_s3_region_name'),
        }),
        ('Local Storage Configuration', {
            'classes': ('collapse',),
            'fields': ('local_storage_path', 'storage_capacity'),
        }),
    )

@admin.register(DatabaseConfiguration)
class DatabaseConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'db_type', 'is_active', 'backup_enabled', 'last_backup')
    list_filter = ('db_type', 'is_active', 'backup_enabled')
    fieldsets = (
        (None, {
            'fields': ('name', 'db_type', 'is_active')
        }),
        ('Connection Settings', {
            'classes': ('collapse',),
            'fields': ('host', 'port', 'username', 'password'),
        }),
        ('Backup Settings', {
            'classes': ('collapse',),
            'fields': ('backup_enabled', 'backup_frequency', 'backup_retention_days', 'last_backup'),
        }),
    )
    readonly_fields = ('last_backup',)

    def save_model(self, request, obj, form, change):
        if obj.backup_enabled and not obj.last_backup:
            obj.last_backup = timezone.now()
        super().save_model(request, obj, form, change)

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
