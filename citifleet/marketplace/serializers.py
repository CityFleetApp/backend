from rest_framework import serializers

from .models import Car, CarMake, CarModel, CarPhoto, GeneralGood, GoodPhoto, JobOffer, CarColor


class CarMakeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name')
        model = CarMake


class CarModelSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'make')
        model = CarModel


class CarColorSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name')
        model = CarColor


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


class CarIdPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarPhoto
        fields = ('id', 'url')


class CarSerializer(serializers.ModelSerializer):
    make = serializers.ReadOnlyField(source='make.name')
    model = serializers.ReadOnlyField(source='model.name')
    type = serializers.ReadOnlyField(source='get_type_display')
    fuel = serializers.ReadOnlyField(source='get_fuel_display')
    color = serializers.ReadOnlyField(source='color.name')
    dimensions = serializers.SerializerMethodField()
    photos = CarIdPhotoSerializer(many=True)
    owner_name = serializers.ReadOnlyField(source='owner.full_name')

    def get_dimensions(self, obj):
        photo = obj.photos.first()
        if photo:
            return [photo.file.width, photo.file.height]
        else:
            return None

    class Meta:
        fields = ('id', 'make', 'model', 'type', 'color', 'year', 'fuel', 'seats',
                  'price', 'description', 'rent', 'photos', 'dimensions', 'created', 'owner', 'owner_name')
        model = Car


class GoodsIdPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodPhoto
        fields = ('id', 'url')


class GeneralGoodSerializer(serializers.ModelSerializer):
    condition = serializers.ReadOnlyField(source='get_condition_display')
    photos = GoodsIdPhotoSerializer(many=True)
    dimensions = serializers.SerializerMethodField()
    owner_name = serializers.ReadOnlyField(source='owner.full_name')

    def get_dimensions(self, obj):
        photo = obj.photos.first()
        if photo:
            return [photo.file.width, photo.file.height]
        else:
            return None

    class Meta:
        fields = ('id', 'item', 'price', 'condition', 'description', 'photos', 'dimensions', 'created', 'owner', 'owner_name')
        model = GeneralGood


class PostingGeneralGoodsSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = GeneralGood
        fields = ('id', 'item', 'price', 'condition', 'description', 'photos')

    def create(self, validated_data):
        photos_data = validated_data.pop('photos')
        goods = GeneralGood.objects.create(**validated_data)
        for photo_data in photos_data:
            GoodPhoto.objects.create(goods=goods, file=photo_data)
        return goods

    def validate(self, attrs):
        attrs['owner'] = self.context['request'].user
        return attrs


class MarketplaceJobOfferSerializer(serializers.ModelSerializer):
    job_type = serializers.ReadOnlyField(source='get_job_type_display')
    vehicle_type = serializers.ReadOnlyField(source='get_vehicle_type_display')
    status = serializers.ReadOnlyField(source='get_status_display')
    awarded = serializers.SerializerMethodField()
    requested = serializers.SerializerMethodField()
    personal = serializers.ReadOnlyField(source='get_personal_display')
    owner_name = serializers.ReadOnlyField(source='owner.full_name')

    def get_awarded(self, obj):
        return obj.driver == self.context['request'].user
    
    def get_requested(self, obj):
        return obj.driver_requests.filter(id=self.context['request'].user.id).exists()

    class Meta:
        model = JobOffer
        fields = ('id', 'title', 'pickup_datetime', 'pickup_address', 'destination', 'fare',
                  'gratuity', 'vehicle_type', 'suite', 'job_type', 'instructions',
                  'status', 'created', 'awarded', 'requested', 'tolls', 'personal',
                  'owner', 'owner_name')


class PostingJobOfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobOffer
        fields = ('id', 'title', 'pickup_datetime', 'pickup_address', 'destination', 'fare',
                  'gratuity', 'vehicle_type', 'suite', 'job_type', 'instructions', 'tolls', 'personal')

    def validate(self, attrs):
        attrs['owner'] = self.context['request'].user
        return attrs


class CarPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'file', 'car')
        model = CarPhoto


class GoodsPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'file', 'goods')
        model = GoodPhoto


class CompleteJobSerializer(serializers.Serializer):
    rating = serializers.IntegerField()
    paid_on_time = serializers.BooleanField()
