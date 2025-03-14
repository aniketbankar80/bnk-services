import os
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    custom_domain = None  # This will be set from settings.AWS_S3_CUSTOM_DOMAIN

    def get_default_settings(self):
        defaults = super().get_default_settings()
        defaults['AWS_S3_OBJECT_PARAMETERS'] = {
            'CacheControl': 'max-age=86400',
            'ContentDisposition': 'inline',
        }
        return defaults

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'private'
    file_overwrite = False
    
    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system."""
        # If the filename already exists, add an underscore and a random 7 character
        # alphanumeric string to the filename before the extension
        import uuid
        
        name = str(name)
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        
        while self.exists(name):
            unique_string = str(uuid.uuid4())[:7]
            name = os.path.join(
                dir_name,
                f'{file_root}_{unique_string}{file_ext}'
            )
        return name