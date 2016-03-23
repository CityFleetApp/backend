from rest_framework import serializers

from .models import Car, CarMake, CarModel


class CarMakeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name')
        model = CarMake


class CarModelSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'make')
        model = CarModel


class CarSerializer(serializers.ModelSerializer):
    make = serializers.ReadOnlyField(source='make.name')
    model = serializers.ReadOnlyField(source='model.name')
    type = serializers.ReadOnlyField(source='get_type_display')
    fuel = serializers.ReadOnlyField(source='get_fuel_display')
    photo = serializers.SerializerMethodField()

    def get_photo(self, obj):
        return 'http://citifleet.steelkiwi.com/media/benefits/discount-tire-direct.jpg.1400x900_q85_box-145%2C0%2C2428%2C1468_crop_detail.jpg'

    class Meta:
        fields = ('id', 'make', 'model', 'type', 'color', 'year', 'fuel', 'seats',
                  'price', 'description', 'rent', 'photo')
        model = Car


class CarRentSerializer(CarSerializer):

    def validate(self, attrs):
        attrs = super(CarRentSerializer, self).validate(attrs)
        attrs['rent'] = True
        return attrs


class CarSaleSerializer(CarSerializer):

    def validate(self, attrs):
        attrs = super(CarSaleSerializer, self).validate(attrs)
        attrs['rent'] = False
        return attrs
