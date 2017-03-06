import logging
import re

import magic
from django.core.files.storage import default_storage
from django.db import DatabaseError
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from core.constants import BASE_ERROR_MSG
from core.constants import MAX_MEETINGS
from core.constants import MOSCOW_LAT
from core.constants import MOSCOW_LNG
from core.constants import MOSCKOW_R


from core.exceptions import UploadException
from core.models import User, Meeting, UserPhotos
from core.serializers import MeetingSerializer, JsonResponseSerializer as JRS, UserSerializerExtended, PhotoSerializer
from core.utils import JsonResponse

logger = logging.getLogger(__name__)


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

        if not hasattr(model, 'owner'):
            logger.error('Model {0} does not have a owner, but you use mixin IsStaffOrOwner'.format(model.__name__))
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
        if (self.lat == None or self.lng == None or self.r == None):
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


class UserCreate(UserMixin, generics.CreateAPIView):
    pass


class UserList(UserMixin, generics.ListCreateAPIView):
    pass


class UserDetail(GeneralPermissionMixin, UserMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class MeetingsList(GeneralPermissionMixin, MeetingMixin, generics.ListCreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        count_meetings = Meeting.objects.filter(owner=user).count()
        if count_meetings >= MAX_MEETINGS:
            logger.warning(
                'USER user_id={0} trying to create more than MAX_MEETINGS meetings'.format(self.request.user.id))
            return Response(
                JRS(JsonResponse(status=429, msg="user's trying to create more than MAX_MEETINGS meetings")).data)
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.lat = float(request.GET.get('lat'))
            self.lng = float(request.GET.get('lng'))
            self.r = float(request.GET.get('r'))
        except (ValueError, TypeError):
            self.lat = MOSCOW_LAT
            self.lng = MOSCOW_LNG
            self.r = MOSCKOW_R
        return super().get(request, *args, **kwargs)





class MeetingDetail(GeneralPermissionMixin, MeetingMixin, generics.RetrieveUpdateAPIView):
    pass


class AuthView(ObtainAuthToken):
    pass


class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    url_prefix = 'user-photos'

    storage = default_storage

    def validate_request(self):
        if 'file' not in self.request.data:
            raise UploadException(response=JsonResponse(status=400, msg='error: no file in request'))

    def check_mime_type(self, file_obj):
        mime_type = magic.from_buffer(file_obj.read(), mime=True)

        if not re.match('image/', mime_type):
            raise UploadException(
                response=JsonResponse(status=400, msg='error wrong file mime type: "{}"'.format(mime_type)))

    def save_file(self, filename, file_obj):

        local_path = '{0}/{1}'.format(self.url_prefix, filename)
        self.storage.save(local_path, file_obj)
        full_path = self.storage.url(local_path)

        try:
            photos_cnt = UserPhotos.objects.filter(owner=self.request.user).count()
            if photos_cnt > 0:
                UserPhotos.objects.create(owner=self.request.user, photo=full_path)
            else:
                UserPhotos.objects.create(owner=self.request.user, photo=full_path, is_avatar=True)
        except DatabaseError as e:
            logger.error(
                'Can not save photo for user_id={0}, photo_path: {1}\nError:{2}'.format(self.request.user.id, full_path,
                                                                                        e))

    def put(self, request, filename, format=None):

        self.request = request

        try:
            self.validate_request()

            file_obj = request.data['file']

            self.check_mime_type(file_obj)

            self.save_file(filename, file_obj)

        except UploadException as e:
            return Response(JRS(e.response).data)

        return Response(JRS(JsonResponse(status=204, msg='ok')).data)


class SetAvatar(GeneralPermissionMixin, PhotoMixin, UpdateAPIView):
    def put(self, request, *args, **kwargs):

        obj_pk = kwargs['pk']

        try:

            UserPhotos.objects.filter(owner=self.request.user, is_avatar=True).update(is_avatar=False)

            obj = UserPhotos.objects.get(pk=obj_pk, owner=self.request.user)
            obj.is_avatar = True
            obj.save()

        except UserPhotos.DoesNotExist as e:
            logger.error(
                'User does not exists user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, obj_pk, e))
            return Response(JRS(JsonResponse(status=400, msg='user does not exists')).data)

        except UserPhotos.MultipleObjectsReturned as e:
            logger.error(
                'Duplicate key for user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, obj_pk, e))
            return Response(JRS(JsonResponse(status=500, msg=BASE_ERROR_MSG)).data)

        except DatabaseError as e:
            logger.error(
                'Can not set avatar for user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, obj_pk, e))
            return Response(JRS(JsonResponse(status=500, msg=BASE_ERROR_MSG)).data)

        return Response(JRS(JsonResponse(status=200, msg='ok')).data)
