import magic
import re
from django.conf import settings
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.files.storage import default_storage

from core.exceptions import UploadException
from core.models import User, Meeting
from core.serializers import UserSerializer, MeetingSerializer


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

        if request.user.is_anonymous():
            return False

        object_model = view.model

        try:
            model = object_model.objects.get(pk=view.kwargs['pk'])
        except (object_model.DoesNotExist, KeyError):
            return False

        if request.user.pk == model.owner.pk:
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


class AuthView(ObtainAuthToken):
    pass


class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def validate_request(self):
        if 'file' not in self.request.data:
            raise UploadException(response=Response(status=400, data={'error': 'No file in request'}))

    def check_mime_type(self, file_obj):
        mime_type = magic.from_buffer(file_obj.read(), mime=True)

        if not re.match('image/', mime_type):
            raise UploadException(response=Response(status=400, data={'error': 'Wrong file mime type'}))

    def save_file(self, filename, file_obj):
        default_storage.save(filename, file_obj)

    def put(self, request, filename, format=None):

        self.request = request

        try:
            self.validate_request()

            file_obj = request.data['file']

            self.check_mime_type(file_obj)

            self.save_file(filename, file_obj)

        except UploadException as e:
            return e.response.serialize()

        return Response(status=204).serialize()
