from django.urls import path, include
from . import views
#from .api import Transfer
#from bank_app.views import (RegisterView, LoginView,GenerateOTP, VerifyOTP, ValidateOTP, DisableOTP)



app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    #path('login', views.login_view, name='login'),


    path('dashboard/', views.dashboard, name='dashboard'),
    path('account_details/<int:pk>/', views.account_details, name='account_details'),
    path('transaction_details/<uuid:transaction>/', views.transaction_details, name='transaction_details'),
    path('make_transfer/', views.make_transfer, name='make_transfer'),
    path('make_loan/', views.make_loan, name='make_loan'),
    path('settings/', views.settings, name='settings'),

    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_search_partial/', views.staff_search_partial, name='staff_search_partial'),
    path('staff_customer_details/<int:pk>/', views.staff_customer_details, name='staff_customer_details'),
    path('staff_account_list_partial/<int:pk>/', views.staff_account_list_partial, name='staff_account_list_partial'),
    path('staff_account_details/<int:pk>/', views.staff_account_details, name='staff_account_details'),
    path('staff_new_account_partial/<int:user>/', views.staff_new_account_partial, name='staff_new_account_partial'),
    path('staff_new_customer/', views.staff_new_customer, name='staff_new_customer'),

    #messages
    path('message/', views.message, name='message'),
    path('message_detail/<int:pk>/', views.message_detail, name='message_detail'),

    #API
    path('api/v1/make_transfer/from/', views.transfer_money_from),
    path('api/v1/make_transfer/to/', views.transfer_money_to),
    path('api/v1/credit_acc_validation/', views.credit_acc_validation),
]