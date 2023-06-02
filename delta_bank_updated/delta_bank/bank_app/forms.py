from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account, Message

User = get_user_model()

class TransferForm(forms.Form):
    amount  = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Debit Account Text', max_length=25)
    credit_account = forms.CharField(label='Credit Account Number', max_length=20)
    credit_text = forms.CharField(label='Credit Account Text', max_length=25)

    def clean(self):
        super().clean()

        # Ensure credit account exist
        credit_account = self.cleaned_data.get('credit_account')
        # try:
        #     Account.objects.get(pk=credit_account)
        # except ObjectDoesNotExist:
        #     self._errors['credit_account'] = self.error_class(['Credit account does not exist.'])

        # Ensure positive amount
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self._errors['username'] = self.error_class(['Username already exists.'])
        return self.cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username', disabled=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('rank', 'personal_id', 'phone')

class NewAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('name',)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('receiver', 'content')
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, current_user, is_staff, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        if(is_staff):
            self.fields['receiver'].queryset = User.objects.exclude(is_staff=True).exclude(pk=current_user.pk)
        else:
            self.fields['receiver'].queryset = User.objects.exclude(is_staff=False).exclude(pk=current_user.pk)

#Til csrf token
class Otp_form(forms.Form):
    my_hidden_field = forms.CharField(widget=forms.HiddenInput())

