from chat.models import Confirm
from core.models import User, Meeting, UserPhotos, SocialData
from core.permissions import IsStaffOrOwner
from core.serializers import UserSerializerExtended, MeetingSerializer, PhotoSerializer, \
    ConfirmSerializer, ConfirmExtendedSerializer, SocialSerializer
from core.constants import MEETING_CATEGORIES, MAX_RADIUS
import datetime


class UserMixin(object):
    model = User
    serializer_class = UserSerializerExtended
    queryset = User.objects.all()
    who_can_update = IsStaffOrOwner
    path_to_owner_pk = 'pk'

    def get_object(self):
        pk = self.kwargs.get('pk', None)
        if pk is None:
            pk = self.request.user.pk
        try:
            obj = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise
        return obj


class MeetingMixin(object):
    model = Meeting
    serializer_class = MeetingSerializer
    who_can_update = IsStaffOrOwner
    path_to_owner_pk = 'owner.pk'

    lat = None
    lng = None
    r = None

    category = None

    def get_queryset(self):

        if self.lat is None or self.lng is None or self.r is None:
            return Meeting.objects.all()

        radius = self.r * 1000
        queryset = Meeting.objects.all().extra(
            where=[
                'ST_Distance_Sphere(coordinates, ST_MakePoint({lat},{lng})) <=  {r}'.format(
                    lat=self.lat,
                    lng=self.lng,
                    r=radius
                )
            ]
        )
        if self.category is not None:
            type_id = MEETING_CATEGORIES.get(self.category)[0]
            queryset = queryset.filter(category=type_id)
        if self.gender is not None:
            queryset = queryset.filter(owner__gender=self.gender)
        if self.age_from is not None and self.age_to is not None:
            birth_date_from = datetime.date.today() - datetime.timedelta(days=(self.age_to*365.25))
            birth_date_to = datetime.date.today() - datetime.timedelta(days=(self.age_from*365.25))
            queryset = queryset.filter(owner__birth_date__range=[
                birth_date_from, birth_date_to
            ])
        return queryset


class PhotoMixin(object):
    model = UserPhotos
    serializer_class = PhotoSerializer
    who_can_update = IsStaffOrOwner
    path_to_owner_pk = 'owner.pk'

    def get_queryset(self):
        return UserPhotos.objects.all()


class ConfirmMixin(object):
    model = Confirm
    queryset = Confirm.objects.all()
    serializer_class = ConfirmExtendedSerializer
    who_can_update = IsStaffOrOwner
    path_to_owner_pk = 'meeting.owner.pk'


class ConfirmBasicMixin(ConfirmMixin):
    serializer_class = ConfirmSerializer


class SocialMixin(object):
    model = SocialData
    serializer_class = SocialSerializer
