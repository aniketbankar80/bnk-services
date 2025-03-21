import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from threading import local

# Create a module-level thread local storage
_thread_locals = local()

def set_loan_application_instance(instance):
    """
    Set the loan application instance in thread locals for the storage backend to use.
    This should be called before saving a LoanApplication instance.
    """
    _thread_locals.instance = instance

class LoanDocumentStorage(FileSystemStorage):
    """
    Custom storage backend for loan documents that organizes files in a hierarchical structure:
    media/loan_documents/[Member Name]/[Customer Name]/[filename]
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('location', os.path.join(settings.MEDIA_ROOT, 'media/loan_documents'))
        kwargs.setdefault('base_url', os.path.join(settings.MEDIA_URL, 'media/loan_documents/'))
        super().__init__(*args, **kwargs)
    
    def get_valid_name(self, name):
        """
        Returns a filename that's free of invalid characters.
        """
        return os.path.normpath(self.get_available_name(name))
    
    def generate_filename(self, filename):
        """
        Generates the full filename by joining the member and customer folders with the filename.
        
        This method is called by Django's storage system when saving a file.
        """
        # Get the instance from thread locals if available
        instance = getattr(_thread_locals, 'instance', None)
        
        if instance and hasattr(instance, 'member') and hasattr(instance, 'full_name'):
            # For LoanApplication model
            member_name = slugify(instance.member.get_full_name() or instance.member.username)
            customer_name = slugify(instance.full_name)
            
            # Create the path: member_name/customer_name/filename
            # Use os.path.basename to get just the filename without any path
            filename = os.path.basename(filename)
            path = os.path.join(member_name, customer_name, filename)
            
            # Create the full directory structure in one go with exist_ok=True
            # This is thread-safe and avoids redundant checks
            full_path = os.path.join(self.location, member_name, customer_name)
            os.makedirs(full_path, exist_ok=True)
            
            # Return the normalized path
            return super().generate_filename(path)
        
        # Default behavior if we can't determine the structure
        return super().generate_filename(filename)
    
    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system.
        If the filename already exists, it will add a unique suffix.
        """
        import uuid
        from pathlib import Path
        
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