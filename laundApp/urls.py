from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('homepage/<str:pk>/', views.homePage, name="homePage"),
    path('com_register_form', views.companyRegisterationForm, name="com_register_form"),
    path('otp/', views.otp_view, name='otp'),
    path('dashboard/', views.dashBoard, name='dashboard'),
    path('re_generate_otp/<str:call>/', views.re_generate_otp, name='re_generate_otp'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name="logout"),
    path('services/', views.services, name= 'services'),
    path('serviceList/', views.viewServiceList, name= 'serviceList'),
    path('addServices/', views.saveService, name= 'addServices'),
    path('settings/', views.settings, name= 'settings'),
    path('jsonSave_setting/', views.saveSettings, name= 'jsonSave_setting'),
    path('profile/', views.profile, name= 'profile'),
    path('jsonSaveProfile/', views.saveUpdateProfile, name= 'jsonSaveProfile'),
    path('otp_frm_profile/', views.otpFrmProfile, name= 'otp_frm_profile'),
    path('booking/', views.loadBooking, name='booking'),


    # URLS FOR RESETING PASSWORD THROUGH EMAIL
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="laundApp/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="laundApp/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="laundApp/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="laundApp/password_reset_done.html"), name="password_reset_complete"),
]