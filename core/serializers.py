from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from core.mixins import LocationMixin
from core.models import User, Meeting


class UserSerializer(serializers.ModelSerializer):

    UPDATE_AVAILABLE_FIELDS = ('first_name', 'about', 'username')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'about', 'password', 'username')
        write_only_fields = ('password', )

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr in self.UPDATE_AVAILABLE_FIELDS:
                setattr(instance, attr, value)

        instance.save()

        return instance


class LocationSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'lat': instance.coords[0],
            'lng': instance.coords[1],
        }

    class Meta:
        model = LocationMixin


class MeetingSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        pass

    members = UserSerializer(many=True, required=False)
    owner = UserSerializer(required=False)
    coordinates = LocationSerializer(required=True)

    UPDATE_AVAILABLE_FIELDS = ('title', 'description', 'coordinates')

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
        fields = ('title', 'description', 'owner', 'members', 'coordinates')


class AddMeetingMemberSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        user = self.context['view'].request.user

        instance.members.add(user.id)

        return instance

    class Meta:
        model = Meeting
        fields = ('id', )
