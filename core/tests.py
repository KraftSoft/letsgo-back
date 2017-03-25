import os
from unittest.mock import patch
from PIL import Image
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.test import Client

from chat.models import Confirm
from core.models import User, Meeting
from rest_framework.authtoken.models import Token
from django.contrib.gis.geos import Point
import json
import copy
from core.views import FileUploadView
from core.constants import MAX_MEETINGS
from core.models import UserPhotos

TEST_USER_1 = 'masha'
TEST_USER_PW_1 = '0'

TEST_USER_2 = 'katya'
TEST_USER_PW_2 = '0'

TEST_USER_3 = 'oleg'
TEST_USER_PW_3 = '0'

MEETING_TITLE_1 = 'go drink'
MEETING_DESC_1 = 'Party for everybody :)'

MEETING_TITLE_2 = 'go drink'
MEETING_DESC_2 = 'Party for everybody :)'


def client_creation(username, password):
    test_user = User.objects.create(username=username)
    test_user.set_password(password)
    test_user.save()
    token, _ = Token.objects.get_or_create(user=test_user)
    token_key = token.key
    token = 'Token {}'.format(token_key)
    client = Client(HTTP_AUTHORIZATION=token)
    return client


def check_json(data, fields):
    for field in fields:
        assert field in data, 'Field "{0}" is not returned in response\nResponse data: {1}'.format(field, data)


class AuthUserMixin(object):
    def setUp(self):
        self.test_user = User.objects.create(username=TEST_USER_1)
        self.test_user.set_password(TEST_USER_PW_1)
        self.test_user.save()

        self.token, _ = Token.objects.get_or_create(user=self.test_user)

        self.token_key = self.token.key
        self.token = 'Token {}'.format(self.token_key)

        self.client = Client(HTTP_AUTHORIZATION=self.token)


class MeetingMixin(AuthUserMixin):
    def setUp(self):
        super().setUp()

        point = Point(55.751244, 37.618423)  # Moscow
        self.test_meeting_1 = Meeting.objects.create(title=MEETING_TITLE_1,
                                                     description=MEETING_DESC_1,
                                                     owner=self.test_user,
                                                     coordinates=point)

        self.test_meeting_2 = Meeting.objects.create(title=MEETING_TITLE_2,
                                                     description=MEETING_DESC_2,
                                                     owner=self.test_user,
                                                     coordinates=point)


class ConfirmMixin(MeetingMixin):
    def setUp(self):
        super().setUp()

        self.test_confirm = Confirm.objects.create(meeting=self.test_meeting_1, user=self.test_user)


class UserTests(AuthUserMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_auth_user(self):
        response = self.client.post(reverse('auth'), {'username': TEST_USER_1, 'password': TEST_USER_PW_1})
        fields = ('token',)
        check_json(response.data, fields)
        self.assertEqual(response.data['token'], self.token_key)

    def test_create_user(self):
        response = self.client.post(reverse('user-create'), {'username': TEST_USER_2, 'password': TEST_USER_PW_2})
        fields = ('id', 'username')
        check_json(response.data, fields)

    def test_get_user(self):
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.test_user.pk}))
        fields = ('id', 'first_name', 'about', 'username')
        check_json(response.data, fields)


class MeetingTests(MeetingMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_list_meetings(self):
        response = self.client.get(reverse('meetings-list'), )

        self.assertTrue(isinstance(response.data, list), msg='Data: {}'.format(response.data))

        fields = ('id', 'title', 'description', 'owner')
        check_json(response.data[0], fields)

    def test_meeting_detail(self):
        response = self.client.get(reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}))
        data = response.data

        fields = ('id', 'title', 'description', 'owner', 'subway')
        check_json(data, fields)

        self.assertEqual(data['title'], MEETING_TITLE_1)
        self.assertEqual(data['description'], MEETING_DESC_1)
        self.assertEqual(data['owner']['id'], self.test_meeting_1.owner_id)

    def test_meeting_create(self):
        title = 'test meeting title'
        desc = 'test meeting desc'

        coords = {
            'lat': 43.588348,
            'lng': 39.729996
        }  # Sochi

        request_data = json.dumps({'title': title, 'description': desc, 'coordinates': coords})

        response = self.client.post(reverse('meetings-list'), request_data, content_type='application/json')

        fields = ('id', 'title', 'description', 'owner', 'subway', 'coordinates')

        data = response.data
        check_json(data, fields)

    def create_meeting(self, lat, lng, title, creator=None):
        desc = title + "desk"
        coords = {
            'lat': lat,
            'lng': lng
        }
        request_data = json.dumps({'title': title, 'description': desc, 'coordinates': coords})
        if (creator != None):
            response = creator.post(reverse('meetings-list'), request_data, content_type='application/json')
            return response
        else:
            response = self.client.post(reverse('meetings-list'), request_data, content_type='application/json')
            return response

    def test_meeting_get_inradius(self):
        client1 = client_creation("vasyan", "qwerty")
        client2 = client_creation("petyan", "qwerty")
        for i in range(0, 3):
            response = self.create_meeting(i, i, "title" + str(i), client1)
        for i in range(3, 6):
            response = self.create_meeting(i, i, "title" + str(i), client2)

        test_url = reverse('meetings-list') + "?lng={lng}&lat={lat}&r={r}"
        response = self.client.get(test_url.format(lng=2, lat=2, r=1))
        data = response.data
        self.assertEqual(len(data), 1)
        response = self.client.get(test_url.format(lng=2.2, lat=2.2, r=200))
        data = response.data
        self.assertEqual(len(data), 3)
        response = self.client.get(test_url.format(lng=2.2, lat=2.2, r=10000000000000))
        data = response.data
        self.assertEqual(len(data), 8)

    def test_4_meeting_add(self):
        client1 = client_creation("vasyan", "qwerty")
        for i in range(0, 5):
            response = self.create_meeting(i, i, "title" + str(i), client1)
            data = response.data
            status_code = data.get('status', None)
            if i < MAX_MEETINGS:
                self.assertEqual(response.status_code, 201)
            else:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(status_code, 429)

    def test_meeting_get_baddata(self):
        test_url = reverse('meetings-list') + "?lng={lng}&lat={lat}&r={r}"
        response = self.client.get(test_url.format(lng="kek", lat=2.2, r="lol"))
        data = response.data
        response_all = self.client.get(reverse('meetings-list'))
        data_all = response_all.data
        self.assertEqual(len(data), len(data_all))


class UpdateMeetingCases(MeetingMixin, TransactionTestCase):
    NEW_MEET_TITLE = 'New meeting title'

    NEW_MEET_DESC = 'New meeting desc'

    LUBERTSY_LAT = 55.688713
    LUBERTSY_LNG = 37.901073

    coords = {
        'lat': LUBERTSY_LAT,
        'lng': LUBERTSY_LNG
    }

    def setUp(self):
        super().setUp()

    def test_update_user(self):
        NEW_USER_NAME = 'july'
        NEW_ABOUT = 'bla bla bla'
        NEW_FN = 'Юля'

        response = self.client.put(
            reverse('user-detail', kwargs={'pk': self.test_user.pk}),
            json.dumps({
                'username': NEW_USER_NAME,
                'about': NEW_ABOUT,
                'first_name': NEW_FN
            }),
            content_type='application/json',
        )

        fields = ('id', 'first_name', 'about', 'username')

        check_json(response.data, fields)

        self.assertEqual(response.data['username'], NEW_USER_NAME)
        self.assertEqual(response.data['first_name'], NEW_FN)
        self.assertEqual(response.data['about'], NEW_ABOUT)

    def test_update_meeting(self):
        response = self.client.put(
            reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}),
            json.dumps({
                'title': self.NEW_MEET_TITLE,
                'description': self.NEW_MEET_DESC,
                'coordinates': self.coords
            }),
            content_type='application/json',
        )

        data = response.data
        fields = ('id', 'title', 'description', 'coordinates', 'owner')
        check_json(data, fields)
        self.assertEqual(data['title'], self.NEW_MEET_TITLE)
        self.assertEqual(data['description'], self.NEW_MEET_DESC)
        self.assertTrue(isinstance(data['coordinates'], dict))
        self.assertEqual(data['coordinates']['lat'], self.LUBERTSY_LAT)
        self.assertEqual(data['coordinates']['lng'], self.LUBERTSY_LNG)

    def test_invalid_user(self):
        client = copy.copy(self.client)
        client.defaults["HTTP_AUTHORIZATION"] = "228"

        response = client.put(
            reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}),
            json.dumps({
                'title': self.NEW_MEET_TITLE,
                'description': self.NEW_MEET_DESC,
                'coordinates': self.coords
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_wrong_user(self):
        ##user 3
        test_user3 = User.objects.create(username=TEST_USER_3)
        test_user3.set_password(TEST_USER_PW_3)
        test_user3.save()

        token3, _ = Token.objects.get_or_create(user=test_user3)
        token_key3 = token3.key
        token3 = 'Token {}'.format(token_key3)

        # Client is standart Django Client
        client3 = Client(HTTP_AUTHORIZATION=token_key3)

        response = client3.put(
            reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}),
            json.dumps({
                'title': self.NEW_MEET_TITLE,
                'description': self.NEW_MEET_DESC,
                'coordinates': self.coords
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class UpdateConfirmCases(ConfirmMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()

    def test_approve__success(self):
        self.assertFalse(self.test_confirm.is_approved)

        response = self.client.put(
            reverse('confirm-action', kwargs={'pk': self.test_confirm.pk}),
            json.dumps({
                'is_approved': True,
            }),
            content_type='application/json',
        )

        code = response.status_code

        self.assertEqual(code, 200)

        confirm = Confirm.objects.get(pk=self.test_confirm.pk)

        self.assertTrue(confirm.is_approved)

    def test_reject__success(self):
        self.assertFalse(self.test_confirm.is_rejected)

        response = self.client.put(
            reverse('confirm-action', kwargs={'pk': self.test_confirm.pk}),
            json.dumps({
                'is_rejected': True,
            }),
            content_type='application/json',
        )

        code = response.status_code

        self.assertEqual(code, 200)

        confirm = Confirm.objects.get(pk=self.test_confirm.pk)

        self.assertTrue(confirm.is_rejected)


class UploadDeletePhotoTest(AuthUserMixin, TestCase):
    def create_photo(self, file_name):
        image = Image.new('RGBA', size=(50, 50), color=(150, 150, 0))
        image.save(file_name)

        response = self.client.put(
            reverse('upload-photo', kwargs={'filename': file_name}),
            data=image,
            accept_encoding='gzip, deflate',
            content_type=False,
        )

	return response


    def test_upload__ok(self):
        file_name = 'test.jpeg'
        response = self.create_photo(file_name)
        data = response.data
        self.assertEqual(data['status'], 204)
        os.remove(file_name)

    def test_delete(self):
        file_name = 'kek.jpeg'
        response_cr = self.create_photo(file_name)
        photos = list(UserPhotos.objects.all())
        kek_id = photos[0].id
        response = self.client.delete(reverse('delete-photo', kwargs={'pk': kek_id}))
        data = response.data
        self.assertEqual(data['status'], 204)
        os.remove(file_name)
