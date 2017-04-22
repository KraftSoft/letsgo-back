import logging
import os
import re

import magic
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import DatabaseError
from django.utils.timezone import datetime
import json

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.generics import UpdateAPIView, CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from chat.models import Confirm
from core.constants import BASE_ERROR_MSG, MAX_MEETINGS,\
    MOSCOW_LAT, MOSCOW_LNG, MAX_RADIUS, MEETING_CATEGORIES, MALE, FEMALE

from core.exceptions import UploadException
from core.mixins import UserMixin, MeetingMixin, PhotoMixin, ConfirmMixin, ConfirmBasicMixin
from core.models import Meeting, UserPhotos, User
from core.permissions import GeneralPermissionMixin
from core.serializers import JsonResponseSerializer as JRS, AuthSerializer
from core.utils import JsonResponse, build_absolute_url

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'users': reverse('user-list', request=request),
    })


class UserList(UserMixin, generics.ListCreateAPIView):
    pass


class UserDetail(GeneralPermissionMixin, UserMixin, generics.RetrieveUpdateDestroyAPIView):
        def dispatch(self, request, *args, **kwargs):
            if 'pk' not in self.kwargs:
                self.kwargs['pk'] = request.user.pk
            return super().dispatch(request, *args, **kwargs)

        def get(self, request, *args, **kwargs):
            try:
                return self.retrieve(request, *args, **kwargs)
            except User.DoesNotExist:
                return Response(JRS(JsonResponse(
                    status=400, msg='User does not exist')).data)


class MeetingsList(GeneralPermissionMixin, MeetingMixin, generics.ListCreateAPIView):

    def __init__(self):
        super().__init__()
        self.lat = None
        self.lng = None
        self.r = None

        self.age_from = None
        self.age_to = None

        self.gender = None

        self.category = None

    def post(self, request, *args, **kwargs):
        user = request.user
        date_create = datetime.today()
        count_meetings = Meeting.objects.filter(owner=user, date_create__date=date_create)\
            .count()
        if count_meetings >= MAX_MEETINGS:
            logger.warning(
                'USER user_id={0} trying to create more than MAX_MEETINGS per day {1}'
                'meetings'.format(self.request.user.id, date_create))
            return Response(
                JRS(JsonResponse(status=429, msg="user's trying to create more than "
                                                 "MAX_MEETINGS meetings")).data)
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.lat = float(request.GET.get('lat'))
            self.lng = float(request.GET.get('lng'))
            self.r = float(request.GET.get('r'))
            if self.r > MAX_RADIUS:
                self.r = MAX_RADIUS
        except ValueError:
            self.lat = MOSCOW_LAT
            self.lng = MOSCOW_LNG
            self.r = MAX_RADIUS
        except TypeError:
            pass

        try:
            self.age_from = int(request.GET.get('age_from'))
            self.age_to = int(request.GET.get('age_to'))
        except (ValueError, TypeError):
            pass

        try:
            self.gender = int(request.GET.get('gender'))
            if self.gender not in (MALE, FEMALE):
                self.gender = None
        except (ValueError, TypeError):
            pass

        category = request.GET.get('category')
        self.category = category if category in MEETING_CATEGORIES else None
        return super().get(request, *args, **kwargs)


class MeetingDetail(GeneralPermissionMixin, MeetingMixin, generics.RetrieveUpdateAPIView):
    pass


class AuthView(ObtainAuthToken):
    serializer_class = AuthSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'href': build_absolute_url(reverse('user-detail', kwargs={'pk': user.pk}))
        })


class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    url_prefix = 'user-photos'

    storage = default_storage

    view_context = {}

    def validate_request(self):
        if 'file' not in self.request.data:
            raise UploadException(response=JsonResponse(status=400, msg='error: no file in request'))

    def check_mime_type(self, file_obj):

        mime_type = magic.from_file(file_obj.name, mime=True)
        if not re.match('image/', mime_type):
            raise UploadException(
                response=JsonResponse(status=400, msg='error wrong file mime type: "{}"'.format(mime_type)))

    def save_file(self, filename, file_obj):

        local_path = '{0}/{1}'.format(self.url_prefix, filename)
        self.view_context['path'] = '{0}{1}'.format(settings.MEDIA_URL, self.storage.save(local_path, file_obj))

        try:
            photos_cnt = UserPhotos.objects.filter(owner=self.request.user).count()
            if photos_cnt > 0:
                UserPhotos.objects.create(owner=self.request.user, photo=self.view_context['path'])
            else:
                UserPhotos.objects.create(owner=self.request.user, photo=self.view_context['path'], is_avatar=True)
        except DatabaseError as e:
            logger.error(
                'Can not save photo for user_id={0}, photo_path: {1}\nError:{2}'.format(
                    self.request.user.id,
                    self.view_context['path'],
                    e
                )
            )

    def put(self, request, filename, format=None):
        self.request = request
        try:
            self.validate_request()
            file_obj = request.data['file']
            # допилить
            self.check_mime_type(file_obj)

            self.save_file(filename, file_obj)

        except UploadException as e:
            return Response(JRS(e.response).data)

        return Response(
            JRS(
                JsonResponse(
                    status=204,
                    msg='ok',
                    data={
                        'href': build_absolute_url(self.view_context['path'])
                    }
                )
            ).data
        )


class DeletePhoto(GeneralPermissionMixin, PhotoMixin, DestroyAPIView):
    parser_classes = (FileUploadParser,)
    url_prefix = 'user-photos'
    storage = default_storage

    def delete(self, request, *args, **kwargs):
        id = kwargs['pk']
        file_path = None
        try:
            target_photo = UserPhotos.objects.get(owner=self.request.user, id=id)
            file_path = target_photo.photo
            UserPhotos.objects.filter(owner=self.request.user, id=id).delete()

        except OSError as e:
            logger.error(
                'Path to file does not exist file={0}\nError: {1}'.format(file_path, e))
            return Response(JRS(JsonResponse(status=400, msg='Path to file does not exist')).data)

        except UserPhotos.DoesNotExist as e:
            logger.error(
                'User does not exists user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, id, e))
            return Response(JRS(JsonResponse(status=400, msg='user does not exists')).data)

        except UserPhotos.MultipleObjectsReturned as e:
            logger.error(
                'Duplicate key for user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, id, e))
            return Response(JRS(JsonResponse(status=500, msg=BASE_ERROR_MSG)).data)

        except DatabaseError as e:
            logger.error(
                'Can not set avatar for user_id={0}, photo_id: {1}\nError: {2}'.format(self.request.user.id, id, e))
            return Response(JRS(JsonResponse(status=500, msg=BASE_ERROR_MSG)).data)

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


class ConfirmCreate(GeneralPermissionMixin, CreateAPIView):
    def create(self, request, *args, **kwargs):

        meeting_pk = kwargs['pk']
        try:
            meeting = Meeting.objects.get(pk=meeting_pk)
        except Meeting.DoesNotExist:
            return Response(JRS(JsonResponse(status=404, msg='meeting does not exist')).data)

        check_confirm = Confirm.objects.filter(meeting_id=meeting_pk, user=request.user).exists()
        if check_confirm:
            return Response(JRS(JsonResponse(status=400, msg='you cannot create more than one confirm')).data)

        if meeting.owner_id == request.user.id:
            return Response(JRS(JsonResponse(status=400, msg='you can not confirm to your event')).data)

        Confirm.objects.create(meeting=meeting, user=request.user)

        return Response(JRS(JsonResponse(status=200, msg='ok')).data)


class ConfirmsList(GeneralPermissionMixin, ConfirmMixin, ListAPIView):
    def get(self, request, *args, **kwargs):
        self.queryset = Confirm.objects.filter(
            meeting__owner=request.user, is_approved=False, is_rejected=False)
        self.queryset.update(is_read=True)
        return super().get(request, *args, **kwargs)


class AcceptConfirm(GeneralPermissionMixin, ConfirmBasicMixin, UpdateAPIView):
    pass


class MeetingTypes(GeneralPermissionMixin, ListAPIView):
    def get(self, request, *args, **kwargs):
        answer = []
        for k, v in MEETING_CATEGORIES.items():
            answer.append((k, v[0]))
        json_data = json.dumps(answer)
        return Response(JRS(JsonResponse(status=200, msg='ok', data=json_data)).data)


class UnreadConfirms(GeneralPermissionMixin, ListAPIView):
    def get(self, request, *args, **kwargs):
        count = Confirm.objects.filter(meeting__owner=request.user, is_read=False).count()
        answer = {"unread": count}
        return Response(JRS(JsonResponse(status=200, msg='ok', data=answer)).data)
