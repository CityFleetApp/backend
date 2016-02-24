from factory import DjangoModelFactory, Faker

from .models import Accounting


class AccountingFactory(DjangoModelFactory):
    name = Faker('name')
    years_of_experience = 1
    rating = 5
    phone = Faker('phone_number')
    address = Faker('address')

    class Meta:
        model = Accounting
