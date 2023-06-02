import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bank_app.models import Account, Ledger, Customer
User = get_user_model()


class Command(BaseCommand):
    def handle(self, **options):

        print('Adding demo data ...')

        bank_user = User.objects.create_user('bank', email='', password=secrets.token_urlsafe(64))
        bank_user.is_active = False
        bank_user.save()
        ipo_account = Account.objects.create(user=bank_user, account_number = 80750000001, name='Bank IPO Account')
        ops_account = Account.objects.create(user=bank_user, account_number = 80750000002, name='Bank OPS Account')
        Ledger.transfer(
            10_000_000,
            ipo_account,
            'Operational Credit',
            ops_account,
            'Operational Credit',
            is_loan=True
        )

        evelyn_user = User.objects.create_user("evelyn", email="evelyn@smith.com", password="keaumulig123")
        evelyn_user.first_name = "Evelyn"
        evelyn_user.last_name = "Smith"
        evelyn_user.save()
        evelyn_customer = Customer(user=evelyn_user, personal_id='00010001', phone='87351233')
        evelyn_customer.save()
        evelyn_account = Account(user=evelyn_user, account_number = 80754002251, name="Main account") 
        evelyn_account.save()

        soren_user = User.objects.create_user("soren", email="sorenraben@hotmail.com", password="keaumulig123")
        soren_user.first_name = "Søren"
        soren_user.last_name = "Raben"
        soren_user.save()
        soren_customer = Customer(user=soren_user, personal_id='00010003', phone='51245682')
        soren_customer.save()
        soren_account = Account(user=soren_user, account_number = 80753401922, name="Main account") 
        soren_account.save()

        Ledger.transfer(
            1_000,
            ops_account,
            'Payout to dummy',
            evelyn_account,
            'Payout from bank'
        )

        paul_user = User.objects.create_user("paul", email="paul@jackson.com", password="keaumulig123")
        paul_user.first_name = "Paul"
        paul_user.last_name = "Jackson"
        paul_user.save()
        paul_customer = Customer(user=paul_user, personal_id='00010002', phone='20456123')
        paul_customer.save()
        paul_account = Account(user=paul_user, account_number = 80759201458, name='Main account')
        paul_account.save()

        #staff
        thomas_user = User.objects.create_user("Thomas", email="thomas@deltabank.com", password="keaumulig123")
        thomas_user.first_name = "Thomas"
        thomas_user.last_name = "Frank"
        thomas_user.is_staff = True
        thomas_user.save()

        #admin
        admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='keaumulig123')
        admin_user.save()