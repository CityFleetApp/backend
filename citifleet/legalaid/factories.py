from factory import DjangoModelFactory, Faker

from .models import InsuranceBroker, Accounting, DMVLawyer, TLCLawyer, Location


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


class DMVLawyerFactory(LegalAidBaseFactory):

    class Meta:
        model = DMVLawyer


class TLCLawyerFactory(LegalAidBaseFactory):

    class Meta:
        model = TLCLawyer


class LocationFactory(DjangoModelFactory):

    class Meta:
        model = Location
