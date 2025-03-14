from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Import related URLs
    path('import-help/', views.import_help, name='import_help'),
    path('download-sample-csv/', views.download_sample_csv, name='download_sample_csv'),
    path('download-sample-excel/', views.download_sample_excel, name='download_sample_excel'),
    # Edit URLs
    path('loan-application/<uuid:loan_id>/edit/', views.edit_loan_application, name='edit_loan'),
    path('loan-application/<uuid:loan_id>/delete/', views.delete_loan_application, name='delete_loan'),
    path('loan-application/<uuid:loan_id>/', views.view_loan, name='view_loan'),
    path('payout-request/<int:payout_id>/edit/', views.edit_payout_request, name='edit_payout'),
    path('payout-request/<int:payout_id>/delete/', views.delete_payout_request, name='delete_payout'),
    path('payout-request/<int:payout_id>/', views.view_payout, name='view_payout'),
    path('loan-document/<uuid:loan_id>/', views.serve_loan_document, name='serve_loan_document'),
    path('payout-screenshot/<int:payout_id>/', views.serve_payout_screenshot, name='serve_payout_screenshot'),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('loan-application/', views.loan_application, name='loan_application'),
    path('payout-request/', views.payout_request, name='payout_request'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='members/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='members/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='members/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='members/password_reset_complete.html'), name='password_reset_complete'),
]