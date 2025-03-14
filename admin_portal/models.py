from django.db import models
from django.core.validators import MinValueValidator

class StorageConfiguration(models.Model):
    STORAGE_TYPES = [
        ('local', 'Local Storage'),
        ('s3', 'AWS S3'),
        ('other', 'Other Storage')
    ]

    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPES, default='local')
    is_active = models.BooleanField(default=False)
    
    # AWS S3 Configuration
    aws_access_key_id = models.CharField(max_length=255, blank=True, null=True)
    aws_secret_access_key = models.CharField(max_length=255, blank=True, null=True)
    aws_storage_bucket_name = models.CharField(max_length=255, blank=True, null=True)
    aws_s3_region_name = models.CharField(max_length=50, blank=True, null=True)
    
    # Local Storage Configuration
    local_storage_path = models.CharField(max_length=255, blank=True, null=True)
    storage_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Storage capacity in GB',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Storage Configuration'
        verbose_name_plural = 'Storage Configurations'

    def __str__(self):
        return f'{self.storage_type} Storage Configuration'

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other configurations
            StorageConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class DatabaseConfiguration(models.Model):
    DB_TYPES = [
        ('sqlite', 'SQLite'),
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('other', 'Other')
    ]

    db_type = models.CharField(max_length=20, choices=DB_TYPES, default='sqlite')
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    
    # Backup Configuration
    backup_enabled = models.BooleanField(default=False)
    backup_frequency = models.PositiveIntegerField(
        help_text='Backup frequency in hours',
        default=24,
        validators=[MinValueValidator(1)]
    )
    backup_retention_days = models.PositiveIntegerField(
        help_text='Number of days to retain backups',
        default=30,
        validators=[MinValueValidator(1)]
    )
    last_backup = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Database Configuration'
        verbose_name_plural = 'Database Configurations'

    def __str__(self):
        return f'{self.name} ({self.db_type})'

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other configurations
            DatabaseConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
