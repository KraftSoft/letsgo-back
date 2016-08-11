from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, AllowAny, BasePermission
from rest_framework.reverse import reverse
from rest_framework.response import Response

from core.models import User, Meeting
from core.serializers import UserSerializer, MeetingSerializer, AddMeetingMemberSerializer


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'users': reverse('user-list', request=request),
    })


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True


class IsStaffOrTargetUser(IsStaff):
    def has_permission(self, request, view):

        if request.user.pk == view.kwargs.get('pk'):
            return True

        return super().has_permission(request, view)


class IsStaffOrOwner(BasePermission):
    def has_permission(self, request, view):
        owner = view.model.owner
        if request.user.pk == owner.pk:
            return True
        return super().has_permission(request, view)


class GeneralPermissionMixin(object):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method == 'POST':
            return [AllowAny()]
        else:
            return [self.who_can_update()]


class UserMixin(object):
    model = User
    serializer_class = UserSerializer
    who_can_update = IsStaffOrTargetUser
    queryset = User.objects.all()


class AddMemberMixin(object):
    model = Meeting
    serializer_class = AddMeetingMemberSerializer
    queryset = Meeting.objects.all()  # TODO remove queryset

    permission_classes = [
        permissions.AllowAny
    ]


class MeetingMixin(object):
    model = Meeting
    serializer_class = MeetingSerializer
    who_can_update = IsStaffOrOwner

    queryset = Meeting.objects.all()


class UserCreate(UserMixin, generics.CreateAPIView):
    pass


class UserList(UserMixin, generics.ListCreateAPIView):
    pass


class UserDetail(GeneralPermissionMixin, UserMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class MeetingsList(MeetingMixin, generics.ListCreateAPIView):
    pass


class MeetingDetail(GeneralPermissionMixin, MeetingMixin, generics.RetrieveUpdateAPIView):
    pass


# TODO lost only update view
class MeetingAddMember(AddMemberMixin, generics.RetrieveUpdateAPIView):
    pass
