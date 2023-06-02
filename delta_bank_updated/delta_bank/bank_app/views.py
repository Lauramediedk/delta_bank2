from decimal import Decimal
from secrets import token_urlsafe
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import IntegrityError
from .forms import TransferForm, UserForm, CustomerForm, NewUserForm, NewAccountForm, MessageForm, Otp_form
from .models import Account, Ledger, Customer, Message, User
from .errors import InsufficientFunds
from .serializers import UserSerializer
import pyotp
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

User = get_user_model()


@login_required
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('bank_app:staff_dashboard'))
    else:
        return HttpResponseRedirect(reverse('bank_app:dashboard'))


# Customer views

@login_required
def dashboard(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    accounts = request.user.customer.accounts
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank_app/dashboard.html', context)


@login_required
def account_details(request, pk):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    account = get_object_or_404(Account, user=request.user, pk=pk)
    context = {
        'account': account,
    }
    return render(request, 'bank_app/account_details.html', context)


@login_required
def transaction_details(request, transaction):
    movements = Ledger.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    context = {
        'movements': movements,
    }
    return render(request, 'bank_app/transaction_details.html', context)


@login_required
def make_transfer(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    form = TransferForm()
    form.fields['debit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/make_transfer.html', context)


@login_required
def make_loan(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    if not request.user.customer.can_make_loan:
        context = {
            'title': 'Create Loan Error',
            'error': 'Loan could not be completed.'
        }
        return render(request, 'bank_app/error.html', context)
    if request.method == 'POST':
        request.user.customer.make_loan(Decimal(request.POST['amount']), request.POST['name'])
        return HttpResponseRedirect(reverse('bank_app:dashboard'))
    return render(request, 'bank_app/make_loan.html', {})


# Staff views

@login_required
def staff_dashboard(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    return render(request, 'bank_app/staff_dashboard.html')


@login_required
def staff_search_partial(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    search_term = request.POST['search_term']
    customers = Customer.search(search_term)
    context = {
        'customers': customers,
    }
    return render(request, 'bank_app/staff_search_partial.html', context)


@login_required
def staff_customer_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'GET':
        user_form = UserForm(instance=customer.user)
        customer_form = CustomerForm(instance=customer)
    elif request.method == 'POST':
        user_form = UserForm(request.POST, instance=customer.user)
        customer_form = CustomerForm(request.POST, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
    new_account_form = NewAccountForm()
    context = {
        'customer': customer,
        'user_form': user_form,
        'customer_form': customer_form,
        'new_account_form': new_account_form,
    }
    return render(request, 'bank_app/staff_customer_details.html', context)


@login_required
def staff_account_list_partial(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    accounts = customer.accounts
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank_app/staff_account_list_partial.html', context)


@login_required
def staff_account_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    account = get_object_or_404(Account, pk=pk)
    context = {
        'account': account,
    }
    return render(request, 'bank_app/account_details.html', context)


@login_required
def staff_new_account_partial(request, user):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_account_form = NewAccountForm(request.POST)
        if new_account_form.is_valid():
            Account.objects.create(user=User.objects.get(pk=user), name=new_account_form.cleaned_data['name'])
    return HttpResponseRedirect(reverse('bank_app:staff_customer_details', args=(user,)))


@login_required
def staff_new_customer(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_user_form = NewUserForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if new_user_form.is_valid() and customer_form.is_valid():
            username    = new_user_form.cleaned_data['username']
            first_name  = new_user_form.cleaned_data['first_name']
            last_name   = new_user_form.cleaned_data['last_name']
            email       = new_user_form.cleaned_data['email']
            password    = token_urlsafe(16)
            rank        = customer_form.cleaned_data['rank']
            personal_id = customer_form.cleaned_data['personal_id']
            phone       = customer_form.cleaned_data['phone']
            try:
                user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                )
                print(f'********** Username: {username} -- Password: {password}')
                Customer.objects.create(user=user, rank=rank, personal_id=personal_id, phone=phone)
                return staff_customer_details(request, user.pk)
            except IntegrityError:
                context = {
                    'title': 'Database Error',
                    'error': 'User could not be created.'
                }
                return render(request, 'bank_app/error.html', context)
    else:
        new_user_form = NewUserForm()
        customer_form = CustomerForm()
    context = {
        'new_user_form': new_user_form,
        'customer_form': customer_form,
    }
    return render(request, 'bank_app/staff_new_customer.html', context)

@login_required
def message(request):
    
    if request.method == 'POST':
        sender = request.user
        receiver_id = request.POST.get("receiver")
        receiver = User.objects.get(pk=receiver_id)
        content = request.POST.get("content")
        try :
            Message.objects.create(sender = sender, receiver = receiver, content = content)
            return index(request)
        except IntegrityError:
            context = {
                'title': 'Database Error',
                'error': 'User could not be created.'
            }
            return render(request, 'bank/error.html', context)
       
    else:
        form = MessageForm(current_user=request.user, is_staff=request.user.is_staff)

    messages = Message.objects.filter(receiver=request.user)
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'bank_app/inbox.html', {'form': form, 'messages': messages, 'users': users})

def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    return render(request, 'bank_app/message.html', {'message': message})

@login_required
def settings(request):
    
    form = Otp_form()

    context = {
        'otp_verified': request.user.otp_verified,
        'user_id': request.user.id,
        'email': request.user.email,
        'form': form #Sender for med for at csrf token kan bruges
    }
    return render(request, 'bank_app/settings.html', context)


# --------------API-------------

#Check om credit konto eksisterer før der fortages en overførelse
@api_view(['POST'])
def credit_acc_validation(request):

    if request.method == 'POST':

        credit_account = request.POST['credit_account']
        print(credit_account)
        try:
            if Account.objects.get(pk=credit_account):
                return JsonResponse({"message": "account found"}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "account not found"}, status=403)


#API der fratrækker penge fra senders konto
@api_view(['POST'])
def transfer_money_from(request):

    if request.method == 'POST':
        amount = int(request.POST['amount'])
        debit_account = Account.objects.get(pk=request.POST['debit_account'])
        debit_text = request.POST['debit_text']

        try:
            transfer = Ledger.transfer_from(amount, debit_account, debit_text)
            return JsonResponse({"unique_id": transfer}, status=200) #Sender UUID tilbage til client
        except InsufficientFunds:
            context = {
                'title': 'Transfer Error',
                'error': 'Insufficient funds for transfer.'
            }
            return render(request, 'bank_app/error.html', context)


#API der sætte penge ind på modtagers konto       
@api_view(['POST'])
def transfer_money_to(request):
    
    if request.method == 'POST':
        amount = int(request.POST['amount'])
        credit_account =  Account.objects.get(pk=request.POST['credit_account'])
        credit_text = request.POST['credit_text']
        unique_id = request.POST['unique_id']

        try:
            Ledger.transfer_to(amount, credit_account, credit_text, unique_id)
            return JsonResponse({"message": "money transfered to account"}, status=200)
        except InsufficientFunds:
            context = {
                'title': 'Transfer Error',
                'error': 'Insufficient funds for transfer.'
            }
            return render(request, 'bank_app/error.html', context)