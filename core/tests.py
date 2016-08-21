from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.test import Client
from core.models import User, Meeting
from rest_framework.authtoken.models import Token
from django.contrib.gis.geos import Point
import json


TEST_USER_1 = 'masha'
TEST_USER_PW_1 = '0'

TEST_USER_2 = 'katya'
TEST_USER_PW_2 = '0'

MEETING_TITLE_1 = 'go drink'
MEETING_DESC_1 = 'Party for everybody :)'

MEETING_TITLE_2 = 'go drink'
MEETING_DESC_2 = 'Party for everybody :)'


def check_json(data, fields):
    for field in fields:
        assert field in data, 'Field "{}" is not returned in response\nResponse data: {}'.format(field, data)


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
        self.test_meeting_1 = Meeting.objects.create(title=MEETING_TITLE_1, description=MEETING_DESC_1, owner=self.test_user,
                                                   coordinates=point)

        self.test_meeting_2 = Meeting.objects.create(title=MEETING_TITLE_2, description=MEETING_DESC_2, owner=self.test_user,
                                                   coordinates=point)


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

        fields = ('id', 'title', 'description', 'owner', 'subway')
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

    def test_add_to_meeting(self):
        self.client.put(reverse('add-member', kwargs={'pk': self.test_meeting_1.pk}), content_type='application/json')

        response = self.client.get(reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}))

        data = response.data

        self.assertTrue(isinstance(data, dict))
        self.assertTrue('members' in data)

        has_user = False
        for member in data['members']:
            if member['id'] == self.test_user.id:
                has_user = True

        self.assertTrue(has_user)


class UpdateCases(AuthUserMixin, TransactionTestCase):
    NEW_USER_NAME = 'july'
    NEW_ABOUT = 'bla bla bla'
    NEW_FN = 'Юля'

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_update_user(self):
        response = self.client.put(
            reverse('user-detail', kwargs={'pk': self.test_user.pk}),
            json.dumps({
                'username': self.NEW_USER_NAME,
                'about': self.NEW_ABOUT,
                'first_name': self.NEW_FN
            }),
            content_type='application/json',
        )

        fields = ('id', 'first_name', 'about', 'username')

        check_json(response.data, fields)

        self.assertEqual(response.data['username'], self.NEW_USER_NAME)
        self.assertEqual(response.data['first_name'], self.NEW_FN)
        self.assertEqual(response.data['about'], self.NEW_ABOUT)
