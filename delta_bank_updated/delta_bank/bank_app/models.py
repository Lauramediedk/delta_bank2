from __future__ import annotations
from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth.models import User, AbstractUser
from .errors import InsufficientFunds
from django_otp.models import Device

import uuid

class User(AbstractUser):
    otp_enabled = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    otp_base32 = models.CharField(max_length=255, null=True)
    otp_auth_url = models.CharField(max_length=255, null=True)

class Rank(models.Model):
    name        = models.CharField(max_length=35, unique=True, db_index=True)
    value       = models.IntegerField(db_index=True)

    @classmethod
    def default_rank(cls) -> Rank:
        return cls.objects.all().aggregate(models.Min('value'))['value__min']

    def __str__(self):
        return f'{self.value}:{self.name}'


class Customer(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.PROTECT)
    rank        = models.ForeignKey(Rank, default=2, on_delete=models.PROTECT)
    personal_id = models.IntegerField(db_index=True)
    phone       = models.CharField(max_length=35, db_index=True)

    @property
    def full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(user=self.user)

    @property
    def can_make_loan(self) -> bool:
        return self.rank.value >= settings.CUSTOMER_RANK_LOAN

    @property
    def default_account(self) -> Account:
        return Account.objects.filter(user=self.user).first()

    def make_loan(self, amount, name):
        assert self.can_make_loan, 'User rank does not allow for making loans.'
        assert amount >= 0, 'Negative amount not allowed for loan.'
        loan = Account.objects.create(user=self.user, name=f'Loan: {name}')
        Ledger.transfer(
            amount,
            loan,
            f'Loan paid out to account {self.default_account}',
            self.default_account,
            f'Credit from loan {loan.pk}: {loan.name}',
            is_loan=True
        )

    @classmethod
    def search(cls, search_term):
        return cls.objects.filter(
            Q(user__username__contains=search_term)   |
            Q(user__first_name__contains=search_term) |
            Q(user__last_name__contains=search_term)  |
            Q(user__email__contains=search_term)      |
            Q(personal_id__contains=search_term)      |
            Q(phone__contains=search_term)
        )[:15]

    def __str__(self):
        return f'{self.personal_id}: {self.full_name}'


class Account(models.Model):
    account_number = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, db_index=True)

    class Meta:
        get_latest_by = 'pk'

    @property
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    def __str__(self):
        return f'{self.pk} :: {self.user} :: {self.name}'


class Ledger(models.Model):
    account     = models.ForeignKey(Account, on_delete=models.PROTECT)
    transaction = models.CharField(max_length=50)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp   = models.DateTimeField(auto_now_add=True, db_index=True)
    text        = models.TextField()

    #Bruges internt til overførelser i samme bank
    @classmethod
    def transfer(cls, amount, debit_account, debit_text, credit_account, credit_text, is_loan=False) -> int:
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        with transaction.atomic():
            if debit_account.balance >= amount or is_loan:
                unique_id = uuid.uuid1()
                cls(amount=-amount, transaction=unique_id, account=debit_account, text=debit_text).save()
                cls(amount=amount, transaction=unique_id, account=credit_account, text=credit_text).save()
            else:
                raise InsufficientFunds
        return unique_id

    #modtager penge
    @classmethod
    def transfer_to(cls, amount, credit_account, credit_text, unique_id):
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        cls(amount=amount, transaction=unique_id, account=credit_account, text=credit_text).save()
    
    #sender penge
    @classmethod
    def transfer_from(cls, amount, debit_account, debit_text, is_loan=False) -> int:

        assert amount >= 0, 'Negative amount not allowed for transfer.'
        
        if debit_account.balance >= amount or is_loan:
            unique_id = uuid.uuid1()
            cls(amount=-amount, transaction=unique_id, account=debit_account, text=debit_text).save()           
        else:
            raise InsufficientFunds
        return unique_id

    def __str__(self):
        return f'{self.amount} :: {self.transaction} :: {self.timestamp} :: {self.account} :: {self.text}'

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)