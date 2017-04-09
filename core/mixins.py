from chat.models import Confirm
from core.models import User, Meeting, UserPhotos, SocialData
from core.permissions import IsStaffOrMe, IsStaffOrOwner
from core.serializers import UserSerializerExtended, MeetingSerializer, PhotoSerializer, \
    ConfirmSerializer, ConfirmExtendedSerializer, SocialSerializer
from core.constants import MEETING_CATEGORIES, MAX_RADIUS


class UserMixin(object):
    model = User
    serializer_class = UserSerializerExtended
    queryset = User.objects.all()
    who_can_update = IsStaffOrMe

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
    queryset = Meeting.objects.all()

    lat = None
    lng = None
    r = None

    meeting_type = None

    def get_queryset(self):

        if self.lat is None or self.lng is None or self.r is None:
            return Meeting.objects.all()

        radius = self.r * 1000 if self.r > MAX_RADIUS else MAX_RADIUS
        queryset = Meeting.objects.all().extra(
            where=[
                'ST_Distance_Sphere(coordinates, ST_MakePoint({lat},{lng})) <=  {r}'.format(
                    lat=self.lat,
                    lng=self.lng,
                    r=radius
                )
            ]
        )
        if self.meeting_type is not None:
            type_id = MEETING_CATEGORIES.get(self.meeting_type)[0]
            queryset = queryset.filter(meeting_type=type_id)
        if self.gender is not None:
            queryset = queryset.filter(owner__gender=self.gender)
        return queryset


class PhotoMixin(object):
    model = UserPhotos
    serializer_class = PhotoSerializer
    who_can_update = IsStaffOrOwner

    def get_queryset(self):
        return UserPhotos.objects.all()


class ConfirmMixin(object):
    model = Confirm
    queryset = Confirm.objects.all()
    serializer_class = ConfirmExtendedSerializer
    who_can_update = IsStaffOrOwner
    owner_path = 'meeting.owner'


class ConfirmBasicMixin(ConfirmMixin):
    serializer_class = ConfirmSerializer


class SocialMixin(object):
    model = SocialData
    serializer_class = SocialSerializer
