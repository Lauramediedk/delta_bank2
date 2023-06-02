from . import views
from django.urls import path, include
from mfa_app.views import (RegisterView, LoginView,GenerateOTP, VerifyOTP, ValidateOTP, DisableOTP)  

app_name = "mfa_app"

urlpatterns = [

    path('login', views.login_view, name='login'),
    #2FA
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('otp/generate', GenerateOTP.as_view()),
    path('otp/verify', VerifyOTP.as_view()),
    path('otp/validate', ValidateOTP.as_view()),
    path('otp/disable', DisableOTP.as_view()),
]