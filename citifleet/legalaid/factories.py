from factory import DjangoModelFactory, Faker

from .models import InsuranceBroker, Accounting


class LegalAidBaseFactory(DjangoModelFactory):
    name = Faker('name')
    years_of_experience = 1
    rating = 5
    phone = Faker('phone_number')
    address = Faker('address')


class InsuranceBrokerFactory(LegalAidBaseFactory):

    class Meta:
        model = InsuranceBroker


class AccountingFactory(LegalAidBaseFactory):

    class Meta:
        model = Accounting
