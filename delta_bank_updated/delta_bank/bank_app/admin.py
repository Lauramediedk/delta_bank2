from django.contrib import admin
from .models import Rank, Customer, Account, Ledger, Message, User
# Register your models here.
admin.site.register(Rank)
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Ledger)
admin.site.register(Message)
admin.site.register(User)
