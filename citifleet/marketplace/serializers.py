from rest_framework import serializers

from .models import Car, CarMake, CarModel, CarPhoto


class CarMakeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name')
        model = CarMake


class CarModelSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'make')
        model = CarModel

    def validate(self, attrs):
        print(attrs)
        return attrs


class CarPostingSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        fields = ('id', 'make', 'model', 'type', 'color', 'year', 'fuel', 'seats',
                  'price', 'description', 'photos')
        model = Car

    def create(self, validated_data):
        photos_data = validated_data.pop('photos')
        car = Car.objects.create(**validated_data)
        for photo_data in photos_data:
            CarPhoto.objects.create(car=car, file=photo_data)
        return car

    def validate(self, attrs):
        attrs['owner'] = self.context['request'].user
        return attrs


class RentCarPostingSerializer(CarPostingSerializer):

    def validate(self, attrs):
        attrs = super(RentCarPostingSerializer, self).validate(attrs)
        attrs['rent'] = True
        return attrs


class SaleCarPostingSerializer(CarPostingSerializer):

    def validate(self, attrs):
        attrs = super(SaleCarPostingSerializer, self).validate(attrs)
        attrs['rent'] = False
        return attrs


class CarSerializer(serializers.ModelSerializer):
    make = serializers.ReadOnlyField(source='make.name')
    model = serializers.ReadOnlyField(source='model.name')
    type = serializers.ReadOnlyField(source='get_type_display')
    fuel = serializers.ReadOnlyField(source='get_fuel_display')
    color = serializers.ReadOnlyField(source='get_color_display')
    photos = serializers.StringRelatedField(many=True)

    class Meta:
        fields = ('id', 'make', 'model', 'type', 'color', 'year', 'fuel', 'seats',
                  'price', 'description', 'rent', 'photos')
        model = Car
