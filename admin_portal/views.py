from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from members.models import LoanApplication, PayoutRequest, MemberProfile
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Calculate key metrics
    total_active_loans = LoanApplication.objects.filter(status='approved').count()
    pending_applications = LoanApplication.objects.filter(status='pending').count()
    total_disbursed = LoanApplication.objects.filter(status='approved').aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    
    # Monthly metrics
    current_month = timezone.now().month
    monthly_applications = LoanApplication.objects.filter(
        created_at__month=current_month
    ).count()
    
    # Member growth
    total_members = User.objects.filter(is_staff=False).count()
    new_members_month = User.objects.filter(
        is_staff=False,
        date_joined__month=current_month
    ).count()
    
    context = {
        'total_active_loans': total_active_loans,
        'pending_applications': pending_applications,
        'total_disbursed': total_disbursed,
        'monthly_applications': monthly_applications,
        'total_members': total_members,
        'new_members_month': new_members_month,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def loan_management(request):
    loans = LoanApplication.objects.all().order_by('-created_at')
    context = {
        'loans': loans,
    }
    return render(request, 'admin/loan_management.html', context)

@login_required
@user_passes_test(is_admin)
def update_loan_status(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        reason = request.POST.get('reason', '')
        if status in ['approved', 'rejected']:
            loan.status = status
            loan.save()
            messages.success(request, f'Loan application {status} successfully.')
        return redirect('loan_management')
    return render(request, 'admin/update_loan_status.html', {'loan': loan})

@login_required
@user_passes_test(is_admin)
def member_management(request):
    members = User.objects.filter(is_staff=False).select_related('memberprofile')
    context = {
        'members': members,
    }
    return render(request, 'admin/member_management.html', context)

@login_required
@user_passes_test(is_admin)
def member_detail(request, member_id):
    member = get_object_or_404(User, id=member_id, is_staff=False)
    loans = LoanApplication.objects.filter(member=member).order_by('-created_at')
    payouts = PayoutRequest.objects.filter(member=member).order_by('-created_at')
    
    context = {
        'member': member,
        'loans': loans,
        'payouts': payouts,
    }
    return render(request, 'admin/member_detail.html', context)
