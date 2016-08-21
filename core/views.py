import hmac
import time
from hashlib import sha256

import six
from django.views.generic import TemplateView
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.response import Response

from core.models import User, Meeting
from core.serializers import UserSerializer, MeetingSerializer, AddMeetingMemberSerializer

from django.conf import settings


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


class IsStaffOrMe(BasePermission):
    def has_permission(self, request, view):
        me = view.model
        if request.user.pk == me.pk:
            return True
        return super().has_permission(request, view)


class GeneralPermissionMixin(object):
    def get_permissions(self):

        if self.request.method == 'DELETE':
            return [IsAdminUser()]

        elif self.request.method == 'GET':  # only authorized users can see objects
            return [IsAuthenticated()]

        elif self.request.method == 'POST':  # only authorized users can create objects
            return [IsAuthenticated()]

        else:
            return [self.who_can_update()]  # only owners can update objects


class UserMixin(object):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()

    who_can_update = IsStaffOrMe


class AddMemberMixin(object):
    model = Meeting
    serializer_class = AddMeetingMemberSerializer
    queryset = Meeting.objects.all()  # TODO remove queryset

    permission_classes = [
        permissions.IsAuthenticated
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


class MeetingsList(GeneralPermissionMixin, MeetingMixin, generics.ListCreateAPIView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeetingDetail(GeneralPermissionMixin, MeetingMixin, generics.RetrieveUpdateAPIView):
    pass


# TODO lost only update view
class MeetingAddMember(GeneralPermissionMixin, AddMemberMixin, generics.RetrieveUpdateAPIView):
    pass


class Centrefugo(TemplateView):
    template_name = 'centrifugo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timestamp'] = str(int(time.time()))

        def generate_token(secret, user, timestamp, info=""):
            sign = hmac.new(six.b(secret), digestmod=sha256)
            sign.update(six.b(user))
            sign.update(six.b(timestamp))
            sign.update(six.b(info))
            return sign.hexdigest()

        context['token'] = generate_token(settings.CENTRIFUGO_KEY, "1", context['timestamp'])

        return context


class AuthView(ObtainAuthToken):
    pass
