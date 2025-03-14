from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from bnk_web.custom_storage import LoanDocumentStorage
from bnk_web.payout_storage import PayoutScreenshotStorage, set_payout_request_instance
import uuid

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    date_of_birth = models.DateField()
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"

    class Meta:
        verbose_name = 'Member Profile'
        verbose_name_plural = 'Member Profiles'

class LoanApplication(models.Model):
    LOAN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal Loan'),
        ('business', 'Business Loan'),
        ('home', 'Home Loan'),
        ('vehicle', 'Vehicle Loan'),
        ('education', 'Education Loan'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    dob = models.DateField()
    contact_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    email = models.EmailField()
    pan_card = models.CharField(max_length=10)
    aadhar_number = models.CharField(max_length=12)
    address = models.TextField()
    income_source = models.CharField(max_length=100)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_tenure = models.IntegerField(help_text='Loan tenure in months')
    purpose = models.TextField()
    dsa_code = models.CharField(max_length=50)
    documents = models.FileField(storage=LoanDocumentStorage())
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Loan Application - {self.full_name} ({self.id})"
    
    def save(self, *args, **kwargs):
        # Set the instance in thread locals for the storage backend to use
        from bnk_web.custom_storage import set_loan_application_instance
        set_loan_application_instance(self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Loan Application'
        verbose_name_plural = 'Loan Applications'
        ordering = ['-created_at']

class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    member = models.ForeignKey(User, on_delete=models.CASCADE)
    dsa_code = models.CharField(max_length=50)
    application_number = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255)
    customer_mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    bank_name = models.CharField(max_length=100)
    disburse_amount = models.DecimalField(max_digits=12, decimal_places=2)
    upi_id = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    customer_pan_card = models.CharField(max_length=10)
    documents = models.FileField(upload_to='payout_documents/', blank=True, null=True)
    application_screenshot = models.ImageField(storage=PayoutScreenshotStorage())
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payout Request - {self.customer_name} ({self.application_number})"
        
    def save(self, *args, **kwargs):
        # Set the instance in thread locals for the storage backend to use
        set_payout_request_instance(self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Payout Request'
        verbose_name_plural = 'Payout Requests'
        ordering = ['-created_at']
