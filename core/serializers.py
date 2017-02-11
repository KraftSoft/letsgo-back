from collections import OrderedDict

from django.contrib.gis.geos import Point
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.settings import api_settings
from core.models import User, Meeting
from core.utils import reverse_full


class SmartUpdaterMixin(object):

    UPDATE_AVAILABLE_FIELDS = tuple()

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr in self.UPDATE_AVAILABLE_FIELDS:
                setattr(instance, attr, value)

        instance.save()

        return instance


class UserSerializer(SmartUpdaterMixin, serializers.ModelSerializer):

    UPDATE_AVAILABLE_FIELDS = ('first_name', 'about', 'username')

    #TODO return avatar
    avatar = SerializerMethodField()
    href = SerializerMethodField()

    def get_avatar(self, obj):
        # TODO remove try-except, it is only for demo
        try:
            return obj.get_avatar()
        except ValueError:
            return ''

    def get_href(self, obj):
        return reverse_full('user-detail', kwargs={'pk': obj.id})

    class Meta:
        model = User
        fields = ('id', 'first_name', 'about', 'password', 'username', 'avatar', 'href')

        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserSerializerExtended(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'about', 'password', 'username', 'avatar', 'photos', 'href')

        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class LocationSerializer(serializers.Field):

    def validate_coordinates(self, coordinates):
        if not isinstance(coordinates, dict):
            raise ValidationError('Invalid request data: coordinates must be an object instance')

        if not 'lat' in coordinates or not 'lng' in coordinates:
            raise ValidationError('Invalid request data: coordinates must contains "lat" and "lng" values')

        try:
            float(coordinates['lat'])
            float(coordinates['lng'])
        except (ValueError, TypeError):
            raise ValidationError('Invalid request data: coordinates must contains "lat" and "lng" values')

    def to_internal_value(self, data):

        if not isinstance(data, dict):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })

        errors = OrderedDict()

        try:
            self.validate_coordinates(data)
        except ValidationError as e:
            errors['coordinates'] = e.detail

        return Point(float(data['lat']), float(data['lng']))

    def to_representation(self, instance):
        return {
            'lat': instance.coords[0],
            'lng': instance.coords[1],
        }


class MeetingSerializer(SmartUpdaterMixin, serializers.ModelSerializer):

    UPDATE_AVAILABLE_FIELDS = ('title', 'description', 'coordinates')

    owner = UserSerializerExtended(required=False)

    coordinates = LocationSerializer(read_only=False)

    def serialize_coordinates(self, instance):
        return {
            'lat': instance.coordinates.coords[0],
            'lng': instance.coordinates.coords[1],
        }

    def create(self, validated_data):

        user = self.context['view'].request.user

        meeting = Meeting.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            coordinates=validated_data['coordinates'],
            owner_id=user.id,
        )
        meeting.save()

        return meeting

    class Meta:
        model = Meeting
        fields = ('id', 'title', 'description', 'owner', 'coordinates', 'subway')


class JsonResponseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    status = serializers.IntegerField()
    msg = serializers.CharField(max_length=512)
