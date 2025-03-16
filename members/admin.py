from django.contrib import admin
from .models import MemberProfile, LoanApplication, PayoutRequest
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Create resource classes for import/export
class MemberProfileResource(resources.ModelResource):
    class Meta:
        model = MemberProfile
        fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name',
                 'phone_number', 'date_of_birth', 'street_address', 'city', 'state', 'zip_code',
                 'profile_picture', 'created_at', 'updated_at')
        export_order = fields

class LoanApplicationResource(resources.ModelResource):
    class Meta:
        model = LoanApplication
        fields = ('id', 'member', 'full_name', 'dob', 'contact_number', 'email', 'pan_card',
                 'aadhar_number', 'address', 'income_source', 'monthly_income', 'loan_type',
                 'loan_amount', 'loan_tenure', 'purpose', 'dsa_code', 'status', 'created_at',
                 'updated_at')
        export_order = fields

class PayoutRequestResource(resources.ModelResource):
    class Meta:
        model = PayoutRequest
        fields = ('id', 'member', 'dsa_code', 'application_number', 'customer_name',
                 'customer_mobile', 'bank_name', 'disburse_amount', 'upi_id', 'location',
                 'customer_pan_card', 'status', 'created_at')
        export_order = fields

@admin.register(MemberProfile)
class MemberProfileAdmin(ImportExportModelAdmin):
    resource_class = MemberProfileResource
    list_display = ('user', 'phone_number', 'city', 'state', 'created_at')
    list_filter = ('city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LoanApplication)
class LoanApplicationAdmin(ImportExportModelAdmin):
    resource_class = LoanApplicationResource
    list_display = ('full_name', 'loan_type', 'loan_amount', 'status', 'created_at')
    list_filter = ('loan_type', 'status')
    search_fields = ('full_name', 'email', 'pan_card', 'aadhar_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_editable = ('status',)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-help/', self.admin_site.admin_view(self.import_help_view),
                 name='loan_application_import_help'),
        ]
        return custom_urls + urls
    
    def import_help_view(self, request):
        from django.shortcuts import render
        return render(request, 'admin/members/loanapplication/import_help.html')
        
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_help'] = True
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(PayoutRequest)
class PayoutRequestAdmin(ImportExportModelAdmin):
    resource_class = PayoutRequestResource
    list_display = ('customer_name', 'application_number', 'disburse_amount', 'status', 'created_at')
    list_filter = ('status', 'bank_name')
    search_fields = ('customer_name', 'application_number', 'customer_pan_card')
    readonly_fields = ('created_at',)
    list_editable = ('status',)
