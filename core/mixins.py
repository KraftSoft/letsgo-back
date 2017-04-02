from chat.models import Confirm
from core.models import User, Meeting, UserPhotos, SocialData
from core.permissions import IsStaffOrMe, IsStaffOrOwner
from core.serializers import UserSerializerExtended, MeetingSerializer, PhotoSerializer, ConfirmSerializer, \
    SocialSerializer


class UserMixin(object):
    model = User
    serializer_class = UserSerializerExtended
    queryset = User.objects.all()

    who_can_update = IsStaffOrMe


class MeetingMixin(object):
    model = Meeting
    serializer_class = MeetingSerializer
    who_can_update = IsStaffOrOwner
    queryset = Meeting.objects.all()
    lat = None
    lng = None
    r = None

    def get_queryset(self):
        if self.lat is None or self.lng is None or self.r is None:
            return Meeting.objects.all()
        radius = self.r * 1000
        query = "select *  from core_meeting where ST_Distance_Sphere(coordinates, ST_MakePoint({lat},{lng})) <=  {r};".format(
            lat=self.lat, lng=self.lng, r=radius)
        return Meeting.objects.raw(query)


class PhotoMixin(object):
    model = UserPhotos
    serializer_class = PhotoSerializer
    who_can_update = IsStaffOrOwner

    def get_queryset(self):
        return UserPhotos.objects.all()


class ConfirmMixin(object):
    model = Confirm
    queryset = Confirm.objects.all()
    serializer_class = ConfirmSerializer
    who_can_update = IsStaffOrOwner
    owner_path = 'meeting.owner'


class SocialMixin(object):
    model = SocialData
    serializer_class = SocialSerializer
