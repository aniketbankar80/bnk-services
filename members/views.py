from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from .models import LoanApplication, PayoutRequest, MemberProfile
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import os
import mimetypes
import csv
import pandas as pd
from io import StringIO
from datetime import datetime

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        exclude = ['member', 'status']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }

class PayoutRequestForm(forms.ModelForm):
    class Meta:
        model = PayoutRequest
        exclude = ['member', 'status']

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'members/home.html')

from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'members/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def import_help(request):
    return render(request, 'members/import_help.html')

def download_sample_csv(request):
    # Create a sample CSV file
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['full_name', 'dob', 'contact_number', 'email', 'pan_card', 'aadhar_number',
                    'address', 'income_source', 'monthly_income', 'loan_type', 'loan_amount',
                    'loan_tenure', 'purpose', 'dsa_code'])
    writer.writerow(['John Doe', '1990-01-31', '9876543210', 'john@example.com', 'ABCDE1234F',
                    '123456789012', '123 Main St, City, State', 'Salary', '50000', 'personal',
                    '500000', '24', 'Home renovation', 'DSA123'])
    
    # Convert string output to bytes before creating response
    output_bytes = output.getvalue().encode('utf-8')
    response = HttpResponse(output_bytes, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loan_application_template.csv"'
    return response

def download_sample_excel(request):
    # Create a sample Excel file
    df = pd.DataFrame({
        'full_name': ['John Doe'],
        'dob': ['1990-01-31'],
        'contact_number': ['9876543210'],
        'email': ['john@example.com'],
        'pan_card': ['ABCDE1234F'],
        'aadhar_number': ['123456789012'],
        'address': ['123 Main St, City, State'],
        'income_source': ['Salary'],
        'monthly_income': [50000],
        'loan_type': ['personal'],
        'loan_amount': [500000],
        'loan_tenure': [24],
        'purpose': ['Home renovation'],
        'dsa_code': ['DSA123']
    })
    
    output = StringIO()
    with pd.ExcelWriter(output.getvalue(), engine='xlsxwriter', mode='wb') as writer:
        df.to_excel(writer, index=False)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="loan_application_template.xlsx"'
    return response

@login_required
def dashboard(request):
    # Get filter parameters from request
    search_query = request.GET.get('search', '').strip()
    loan_type = request.GET.get('loan_type', '').strip()
    status = request.GET.get('status', '').strip()

    # Base queryset
    loan_applications = LoanApplication.objects.filter(member=request.user)
    payout_requests = PayoutRequest.objects.filter(member=request.user)

    # Apply filters
    if search_query:
        loan_applications = loan_applications.filter(
            models.Q(id__icontains=search_query) |
            models.Q(member__username__icontains=search_query) |
            models.Q(full_name__icontains=search_query) |
            models.Q(loan_type__icontains=search_query)
        )

    if loan_type and loan_type.lower() != 'all':
        # Map the display loan type values to the model's stored values
        loan_type_mapping = {
            'personal loan': 'personal',
            'business loan': 'business',
            'home loan': 'home',
            'vehicle loan': 'vehicle',
            'education loan': 'education'
        }
        # Get the model value for the selected loan type (case insensitive)
        model_loan_type = loan_type_mapping.get(loan_type.lower())
        if model_loan_type:
            loan_applications = loan_applications.filter(loan_type=model_loan_type)
        else:
            # Fallback to direct filtering if mapping not found
            loan_applications = loan_applications.filter(loan_type__icontains=loan_type)

    if status and status.lower() != 'all':
        loan_applications = loan_applications.filter(status__iexact=status)

    # Order by created date
    loan_applications = loan_applications.order_by('-created_at')
    payout_requests = payout_requests.order_by('-created_at')

    context = {
        'loan_applications': loan_applications,
        'payout_requests': payout_requests,
        'total_loans': LoanApplication.objects.filter(member=request.user).count(),
        'approved_loans': len(LoanApplication.objects.filter(member=request.user, status='approved')),
        # Add filter values to context for form persistence
        'search_query': search_query,
        'selected_loan_type': loan_type,
        'selected_status': status,
    }
    return render(request, 'members/dashboard.html', context)

@login_required
def loan_application(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            loan_app = form.save(commit=False)
            loan_app.member = request.user
            
            # Set the loan application instance before saving
            from bnk_web.custom_storage import set_loan_application_instance
            set_loan_application_instance(loan_app)
            
            loan_app.save()
            messages.success(request, 'Loan application submitted successfully!')
            return redirect('dashboard')
    else:
        form = LoanApplicationForm()
    return render(request, 'members/loan_application.html', {'form': form})

@login_required
def payout_request(request):
    if request.method == 'POST':
        form = PayoutRequestForm(request.POST, request.FILES)
        if form.is_valid():
            payout = form.save(commit=False)
            payout.member = request.user
            payout.save()
            messages.success(request, 'Payout request submitted successfully!')
            return redirect('dashboard')
    else:
        form = PayoutRequestForm()
    return render(request, 'members/payout_request.html', {'form': form})

@login_required
def profile(request):
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist:
        member_profile = None
    return render(request, 'members/profile.html', {
        'user': request.user,
        'member_profile': member_profile
    })



@login_required
def payout_request(request):
    if request.method == 'POST':
        form = PayoutRequestForm(request.POST, request.FILES)
        if form.is_valid():
            payout_req = form.save(commit=False)
            payout_req.member = request.user
            payout_req.save()
            messages.success(request, 'Payout request submitted successfully!')
            return redirect('dashboard')
    else:
        form = PayoutRequestForm()
    
    return render(request, 'members/payout_request.html', {'form': form})

@login_required
def view_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, member=request.user)
    return render(request, 'members/view_loan.html', {'loan': loan})

@login_required
def edit_loan_application(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, member=request.user)
    
    # Only allow editing if the loan is pending or rejected
    if loan.status not in ['pending', 'rejected']:
        messages.error(request, 'You cannot edit an approved loan application.')
        return redirect('view_loan', loan_id=loan_id)
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, request.FILES, instance=loan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan application updated successfully!')
            return redirect('view_loan', loan_id=loan_id)
    else:
        form = LoanApplicationForm(instance=loan)
    
    return render(request, 'members/loan_application.html', {'form': form, 'is_edit': True})

@login_required
def update_payout_request(request, payout_id):
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    
    if request.method == 'POST':
        form = PayoutRequestForm(request.POST, request.FILES, instance=payout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payout request updated successfully!')
            return redirect('dashboard')
    else:
        form = PayoutRequestForm(instance=payout)
    
    return render(request, 'members/payout_request.html', {'form': form, 'is_edit': True})

def about_view(request):
    return render(request, 'members/about.html')

def contact_view(request):
    return render(request, 'members/contact.html')

@login_required
def serve_loan_document(request, loan_id):
    # Get the loan application and verify ownership
    loan = get_object_or_404(LoanApplication, id=loan_id, member=request.user)
    
    # Ensure the loan has a document
    if not loan.documents:
        messages.error(request, 'No document available for this loan application.')
        return redirect('view_loan', loan_id=loan_id)
    
    # Get the file from storage
    try:
        # Verify file exists and is accessible
        if not loan.documents.storage.exists(loan.documents.name):
            messages.error(request, 'Document file not found.')
            return redirect('view_loan', loan_id=loan_id)

        # Get the file path and name
        file_path = loan.documents.path
        file_name = loan.documents.name
        
        # Use Python's mimetypes module for more accurate MIME type detection
        import mimetypes
        import os
        
        # Get the file extension and ensure it's lowercase
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Get MIME type based on file extension
        content_type, _ = mimetypes.guess_type(file_name)
        
        # Fallback MIME types if guess_type fails
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        
        if not content_type:
            content_type = mime_types.get(file_ext)
        
        # Validate file type
        if not content_type or file_ext not in mime_types:
            messages.error(request, 'Invalid or unsupported document type.')
            return redirect('view_loan', loan_id=loan_id)

        # Verify file size (optional, adjust max_size as needed)
        max_size = 10 * 1024 * 1024  # 10MB
        if os.path.getsize(file_path) > max_size:
            messages.error(request, 'File size exceeds maximum allowed limit.')
            return redirect('view_loan', loan_id=loan_id)
        
        # Open and serve the file with proper error handling
        try:
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_name)}"'
                # Add security headers
                response['X-Content-Type-Options'] = 'nosniff'
                response['Content-Security-Policy'] = "default-src 'self'"
                return response
        except IOError:
            messages.error(request, 'Error reading the document file.')
            return redirect('view_loan', loan_id=loan_id)

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error serving document for loan {loan_id}: {str(e)}')
        
        messages.error(request, 'Error accessing the document. Please try again later.')
        return redirect('view_loan', loan_id=loan_id)

from django.core.files.storage import default_storage
from django.http import FileResponse
from django.views.static import serve
from django.conf import settings
import os

@login_required
def serve_payout_document(request, payout_id):
    # Get the payout request and verify ownership
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    
    # Ensure the payout has a document
    if not payout.documents:
        messages.error(request, 'No document available for this payout request.')
        return redirect('view_payout', payout_id=payout_id)
    
    try:
        # Get the file path relative to MEDIA_ROOT
        file_path = payout.documents.name
        
        # Verify file exists in storage
        if not default_storage.exists(file_path):
            messages.error(request, 'Document file not found.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Get the absolute file path
        absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Verify file type and size
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Define allowed file types
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.txt'}
        
        if file_ext not in allowed_extensions:
            messages.error(request, 'Invalid or unsupported document type.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Check file size (10MB limit)
        if default_storage.size(file_path) > 10 * 1024 * 1024:
            messages.error(request, 'File size exceeds maximum allowed limit.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Open and stream the file using FileResponse
        file = default_storage.open(file_path)
        response = FileResponse(file, content_type=mimetypes.guess_type(file_name)[0] or 'application/octet-stream')
        
        # Set response headers
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error serving document for payout {payout_id}: {str(e)}')
        
        messages.error(request, 'Error accessing the document. Please try again later.')
        return redirect('view_payout', payout_id=payout_id)

def custom_404(request, exception):
    return render(request, 'error/404.html', status=404)

def custom_500(request):
    return render(request, 'error/500.html', status=500)
@login_required
def view_payout(request, payout_id):
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    return render(request, 'members/view_payout.html', {'payout': payout})

@login_required
def serve_payout_screenshot(request, payout_id):
    # Get the payout request and verify ownership
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    
    # Ensure the payout has a screenshot
    if not payout.application_screenshot:
        messages.error(request, 'No screenshot available for this payout request.')
        return redirect('view_payout', payout_id=payout_id)
    
    try:
        # Get the file path relative to storage
        file_path = payout.application_screenshot.name
        
        # Get the storage backend used for this field
        storage = payout.application_screenshot.storage
        
        # Verify file exists in storage
        if not storage.exists(file_path):
            messages.error(request, 'Screenshot file not found.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Verify file type and size
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Define allowed file types
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        
        if file_ext not in allowed_extensions:
            messages.error(request, 'Invalid or unsupported image type.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Check file size (5MB limit)
        if storage.size(file_path) > 5 * 1024 * 1024:
            messages.error(request, 'File size exceeds maximum allowed limit.')
            return redirect('view_payout', payout_id=payout_id)
        
        # Open and stream the file using FileResponse
        file = storage.open(file_path)
        response = FileResponse(file, content_type=mimetypes.guess_type(file_name)[0] or 'application/octet-stream')
        
        # Set response headers
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error serving screenshot for payout {payout_id}: {str(e)}')
        
        messages.error(request, 'Error accessing the screenshot. Please try again later.')
        return redirect('view_payout', payout_id=payout_id)

@login_required
def delete_payout_request(request, payout_id):
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    
    # Only allow deletion if the payout is pending or rejected
    if payout.status not in ['pending', 'rejected']:
        messages.error(request, 'You cannot delete an approved payout request.')
        return redirect('view_payout', payout_id=payout_id)
    
    payout.delete()
    messages.success(request, 'Payout request deleted successfully!')
    return redirect('dashboard')
@login_required
def edit_payout_request(request, payout_id):
    payout = get_object_or_404(PayoutRequest, id=payout_id, member=request.user)
    
    if request.method == 'POST':
        form = PayoutRequestForm(request.POST, request.FILES, instance=payout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payout request updated successfully!')
            return redirect('dashboard')
    else:
        form = PayoutRequestForm(instance=payout)
    
    return render(request, 'members/payout_request.html', {'form': form, 'is_edit': True})

def about(request):
    return render(request, 'members/about.html')

def contact(request):
    return render(request, 'members/contact.html')

@login_required
def delete_loan_application(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, member=request.user)
    
    # Only allow deletion if the loan is pending or rejected
    if loan.status not in ['pending', 'rejected']:
        messages.error(request, 'You cannot delete an approved loan application.')
        return redirect('view_loan', loan_id=loan_id)
    
    if request.method == 'POST':
        loan.delete()
        messages.success(request, 'Loan application deleted successfully!')
        return redirect('dashboard')
    
    return redirect('view_loan', loan_id=loan_id)
