from collections import OrderedDict

from django.contrib.gis.geos import Point
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.settings import api_settings
from django.core.urlresolvers import reverse
from core.constants import MINE, APPROVED, DISAPPROVED

from chat.models import Confirm
from core.models import User, Meeting, UserPhotos, SocialData
from core.utils import reverse_full, build_absolute_url
import hashlib


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

    avatar = SerializerMethodField()
    href = SerializerMethodField()

    def get_avatar(self, obj):
        return obj.get_avatar()

    def get_href(self, obj):
        return reverse_full('user-detail', kwargs={'pk': obj.id})

    class Meta:
        model = User
        fields = ('id', 'first_name', 'about', 'password', 'avatar', 'href')

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'avatar': {'required': False},
            'photos': {'required': False},
        }

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserPhotoSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    delete_photo = serializers.SerializerMethodField()
    set_avatar = serializers.SerializerMethodField()

    def get_delete_photo(self, obj):
        result = reverse('delete-photo', kwargs={'pk':obj.id})
        return build_absolute_url(result)

    def get_set_avatar(self, obj):
        result = reverse('set-avatar', kwargs={'pk':obj.id})
        return build_absolute_url(result)

    def get_photo(self, obj):
        return build_absolute_url(obj.photo)

    class Meta:
        model = UserPhotos
        fields = ('photo', 'delete_photo', 'set_avatar' )


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhotos
        fields = ('is_avatar', )


class UserSerializerExtended(UserSerializer):
    photos = UserPhotoSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'about', 'password', 'username', 'avatar', 'photos', 'href')

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'avatar': {'required': False},
            'photos': {'required': False},
        }


class LocationSerializer(serializers.Field):

    def validate_coordinates(self, coordinates):
        if not isinstance(coordinates, dict):
            raise ValidationError('Invalid request data: coordinates must be an object instance')

        if 'lat' not in coordinates or 'lng' not in coordinates:
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


class ConfirmSerializer(SmartUpdaterMixin, serializers.ModelSerializer):

    UPDATE_AVAILABLE_FIELDS = ('is_approved', 'is_rejected', 'is_read')

    user = UserSerializer(read_only=True)

    class Meta:
        model = Confirm
        fields = ('id', 'user', 'date_create', 'is_approved', 'is_rejected', 'is_read')


class MeetingSerializer(SmartUpdaterMixin, serializers.ModelSerializer):

    UPDATE_AVAILABLE_FIELDS = ('title', 'description', 'coordinates', 'meeting_date')

    owner = UserSerializerExtended(required=False)

    coordinates = LocationSerializer(read_only=False)

    href = serializers.SerializerMethodField()

    confirms = ConfirmSerializer(required=False)

    meeting_date = serializers.DateTimeField(required=True)

    color_status = serializers.SerializerMethodField()

    group_type = serializers.IntegerField(required=True)

    meeting_type = serializers.IntegerField(required=False)

    def get_color_status(self, obj):
        request_user = self.context['request'].user
        if(request_user.id == obj.owner.id):
            return (MINE)
        check_confirm = Confirm.objects.filter(
            user__id=request_user.id, meeting=obj, is_approved=True).exists()
        if check_confirm:
            return APPROVED
        return DISAPPROVED

    def get_href(self, obj):
        return reverse_full('meeting-detail', kwargs={'pk': obj.id})

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
            meeting_date=validated_data['meeting_date'],
            owner_id=user.id,
            group_type=validated_data['group_type'],
            meeting_type=validated_data.get('meeting_type', 0)
        )
        meeting.save()

        return meeting

    class Meta:
        model = Meeting
        fields = ('id', 'title', 'meeting_date', 'description', 'group_type', 'meeting_type',
                  'owner', 'coordinates', 'subway', 'href', 'confirms', 'color_status')


class JsonResponseSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    status = serializers.IntegerField()
    msg = serializers.CharField(max_length=512)
    data = serializers.JSONField(required=False)


class ConfirmExtendedSerializer(ConfirmSerializer):
    meeting = MeetingSerializer(required=False)

    class Meta:
        model = Confirm
        fields = ('id', 'user', 'date_create', 'is_approved', 'is_rejected', 'meeting')


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialData
        fields = ('social_slug', 'external_id', 'token')


class AuthSerializer(serializers.Serializer):

    social_slug = serializers.CharField(max_length=16)
    external_id = serializers.IntegerField()
    token = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=32)

    def validate(self, attrs):

        social_slug = attrs.get('social_slug')
        external_id = attrs.get('external_id')
        token = attrs.get('token')
        first_name = attrs.get('first_name')

        if social_slug and external_id and token and first_name:

            # TODO IT IS NEED TO CHECK TOKEN BY VK
            # AND CHECK THAT USER WITH TOKEN HAVE VK_ID LIKE A external_id
            existing_social_data = SocialData.objects.filter(
                social_slug=social_slug,
                external_id=external_id,
            ).last()

            if existing_social_data:

                existing_social_data.token = token
                existing_social_data.save()

                attrs['user'] = existing_social_data.user
                return attrs

            username = hashlib.sha224('{0}{1}'.format(token, social_slug).encode('utf-8')).hexdigest()[:20]
            user = User.objects.create(first_name=first_name, username=username)
            user.save()

            social = SocialData.objects.create(
                user=user,
                social_slug=social_slug,
                external_id=external_id,
                token=token
            )

            social.save()

            attrs['user'] = user
            return attrs
        else:
            msg = 'Must include "social_slug", "external_id", "first_name" and "token".'
            raise serializers.ValidationError(msg, code='authorization')
