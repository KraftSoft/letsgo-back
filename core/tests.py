import os
import urllib.parse

from PIL import Image
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.test import Client
from django.utils import timezone
import datetime

from chat.models import Confirm
from core.models import User, Meeting, SocialData
from rest_framework.authtoken.models import Token
from django.contrib.gis.geos import Point
import json
import copy
from core.constants import MAX_MEETINGS,\
    MINE, APPROVED, DISAPPROVED, MALE, FEMALE, MEETING_CATEGORIES, MAX_RADIUS, MOSCOW_LAT, MOSCOW_LNG, PITER_LAT, \
    PITER_LNG

from core.models import UserPhotos

timezone.now()

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

MEETING_DATE_1 = timezone.now().date()

PAIR_MEETING = 0
GROUP_MEETING = 1

DEFAULT_BIRTH_DATE = datetime.date(2000, 1, 1)


def client_creation(username, password,
                    birth_date=DEFAULT_BIRTH_DATE, gender=MALE):
    test_user = User.objects.\
        create(username=username, birth_date=birth_date, gender=gender)
    test_user.set_password(password)
    test_user.save()
    token, _ = Token.objects.get_or_create(user=test_user)
    token_key = token.key
    token = 'Token {0}'.format(token_key)
    client = Client(HTTP_AUTHORIZATION=token)
    return client


def check_json(data, fields):
    for field in fields:
        assert field in data, 'Field "{0}" is not returned in response\n' \
                              'Response data: {1}'.format(field, data)


class AuthUserMixin(object):
    def setUp(self):
        self.test_user = User.objects.create(username=TEST_USER_1,
                                             birth_date=DEFAULT_BIRTH_DATE, gender=FEMALE)
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

        self.test_meeting_1 = Meeting.objects.create(
            title=MEETING_TITLE_1,
            description=MEETING_DESC_1,
            owner=self.test_user,
            coordinates=point,
            meeting_date=timezone.now(),
            group_type=GROUP_MEETING
        )

        self.test_meeting_2 = Meeting.objects.create(
            title=MEETING_TITLE_2,
            description=MEETING_DESC_2,
            owner=self.test_user,
            coordinates=point,
            meeting_date=timezone.now(),
            group_type=GROUP_MEETING
        )

    def create_meeting(
            self,
            lat,
            lng,
            title,
            creator=None,
            date=None,
            date_create=None,
            group_type=PAIR_MEETING,
            category=None
    ):

        desc = title + "desk"
        coords = {
            'lat': lat,
            'lng': lng
        }

        if date is None:
            date = timezone.now().date().isoformat()

        if date_create is None:
            request_dict = {
                'title': title,
                'description': desc,
                'group_type': group_type,
                'coordinates': coords,
                'meeting_date': date
            }

        else:
            request_dict = {
                'title': title,
                'description': desc,
                'date_create': date_create,
                'group_type': group_type,
                'coordinates': coords,
                'meeting_date': date
            }

        if category is not None:
            request_dict['category'] = category
        request_data = json.dumps(request_dict)

        if creator is not None:
            response = creator.post(reverse('meetings-list'), request_data, content_type='application/json')
            return response

        response = self.client.post(reverse('meetings-list'), request_data, content_type='application/json')
        return response


class ConfirmMixin(MeetingMixin):
    def setUp(self):
        super().setUp()
        self.test_confirm = Confirm.objects.create(meeting=self.test_meeting_1, user=self.test_user)


class CreateUserTests(TestCase):
    def test_first_login(self):
        response = self.client.post(
            reverse('auth'),
            data={
                'first_name': 'Ilia',
                'social_slug': 'vk',
                'external_id': 228,
                'token': 'like a token'
            }
        )

        check_json(response.data, ('token', 'href'))

    def test_second_login(self):
        first_name = 'Alla'
        ext_id = 11211
        test_token = 'test token'

        user = User.objects.create(first_name=first_name)
        user.save()

        social = SocialData.objects.create(
            user=user,
            social_slug='vk',
            external_id=ext_id,
            token=test_token
        )

        social.save()

        token, _ = Token.objects.get_or_create(user=user)

        response = self.client.post(
            reverse('auth'),
            data={
                'first_name': first_name,
                'social_slug': 'vk',
                'external_id': ext_id,
                'token': test_token
            }
        )

        check_json(response.data, ('token', 'href'))

        self.assertEqual(response.data['token'], user.auth_token.key)


class UserTests(AuthUserMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_get_user(self):
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.test_user.pk}))
        fields = ('id', 'first_name', 'about')
        check_json(response.data, fields)

    def test_get_myself(self):
        resp = self.client.get(reverse('user-detail'))
        self.assertEqual(resp.data['id'], self.test_user.id)


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

        fields = ('id', 'title', 'description', 'owner', 'subway', 'group_type')
        check_json(data, fields)

        self.assertEqual(data['title'], MEETING_TITLE_1)
        self.assertEqual(data['description'], MEETING_DESC_1)
        self.assertEqual(data['owner']['id'], self.test_meeting_1.owner_id)

    def test_meeting_create(self):
        title = 'test meeting title'
        response = self.create_meeting(43.588348, 39.729996, title, self.client)
        fields = ('id', 'title', 'description', 'owner', 'subway',
                  'coordinates', 'meeting_date', 'group_type', 'category')
        data = response.data
        check_json(data, fields)

    def test_meeting_get_inradius(self):

        client1 = client_creation("vasyan", "qwerty")
        client2 = client_creation("petyan", "qwerty")

        for i in range(2):
            self.create_meeting(
                lat=MOSCOW_LAT,
                lng=MOSCOW_LNG,
                title="title" + str(i),
                creator=client1 if i % 2 == 0 else client2
            )

        for i in range(4):
            self.create_meeting(
                lat=PITER_LAT,
                lng=PITER_LNG,
                title="title" + str(i),
                creator=client2 if i % 2 == 0 else client1
            )

        test_url = reverse('meetings-list') + "?lng={lng}&lat={lat}&r={r}"

        response = self.client.get(test_url.format(lat=MOSCOW_LAT, lng=MOSCOW_LNG, r=MAX_RADIUS))
        data = response.data

        for item in data:
            self.assertEqual(item['coordinates']['lat'], MOSCOW_LAT)
            self.assertEqual(item['coordinates']['lng'], MOSCOW_LNG)

        response = self.client.get(test_url.format(lat=PITER_LAT, lng=PITER_LNG, r=MAX_RADIUS))
        data = response.data

        for item in data:
            self.assertEqual(item['coordinates']['lat'], PITER_LAT)
            self.assertEqual(item['coordinates']['lng'], PITER_LNG)

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

    def test_category_filter(self):
        client1 = client_creation("vasyan", "qwerty")
        client2 = client_creation("petya", "qwerty")

        for i in range(0, 4):
            self.create_meeting(
                lat=1,
                lng=1,
                title="title" + str(i),
                creator=client1 if i % 2 == 0 else client2,
                date=None,
                date_create=None,
                group_type=PAIR_MEETING,
                category=MEETING_CATEGORIES['sport'][0]
            )

        self.create_meeting(
            lat=1,
            lng=1,
            title="title",
            creator=client1,
            date=None,
            date_create=None,
            group_type=PAIR_MEETING,
            category=MEETING_CATEGORIES['bar'][0]
        )

        test_url = reverse('meetings-list') + "?lng={0}&lat={1}&r={2}&category={3}"

        response = self.client.get(test_url.format(1, 1, MAX_RADIUS, 'sport'))
        data = response.data
        self.assertEqual(len(data), 4)

        test_url = reverse('meetings-list') + "?lng={0}&lat={1}&r={2}"

        response = self.client.get(test_url.format(1, 1, MAX_RADIUS))
        data = response.data
        self.assertEqual(len(data), 5)

    def test_gender_filter(self):

        client1 = client_creation("vasyan", "qwerty", gender=MALE)
        client2 = client_creation("lena", "qwerty", gender=FEMALE)

        for i in range(6):
            self.create_meeting(
                lat=1,
                lng=1,
                title="title" + str(i),
                creator=client1 if i % 2 == 0 else client2,
                date=None,
                date_create=None,
                group_type=PAIR_MEETING,
                category=MEETING_CATEGORIES['sport'][0]
            )

        test_url = reverse('meetings-list') + "?lng={0}&lat={1}&r={2}&gender={3}"
        meet_with_boys = self.client.get(test_url.format(1, 1, MAX_RADIUS, MALE))
        self.assertEqual(len(meet_with_boys.data), 3)

        test_url = reverse('meetings-list') + "?lng={0}&lat={1}&r={2}&gender={3}"
        meet_with_girls = self.client.get(test_url.format(1, 1, MAX_RADIUS, FEMALE))
        self.assertEqual(len(meet_with_girls.data), 3)

    def test_age_filter(self):

        client1 = client_creation("vasyan", "qwerty", datetime.date(2005, 1, 1))
        client2 = client_creation("ivan", "qwerty")

        for i in range(0, 3):
            self.create_meeting(
                lat=1,
                lng=1,
                title="title" + str(i),
                creator=client1,
                date=None,
                date_create=None,
                group_type=PAIR_MEETING,
                category=MEETING_CATEGORIES['sport'][0]
            )

        self.create_meeting(
            lat=5,
            lng=5,
            title="title" + str(5),
            creator=client2,
            date=None,
            date_create=None,
            group_type=PAIR_MEETING,
            category=MEETING_CATEGORIES['sport'][0]
        )

        test_url = '{0}?{1}'.format(reverse('meetings-list'), urllib.parse.urlencode({
            'lng': 1,
            'lat': 1,
            'r': MAX_RADIUS,
            'gender': MALE,
            'age_from': 0,
            'age_to': 14
        }))

        meet_r = self.client.get(test_url)
        self.assertEqual(len(meet_r.data), 3)


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
        NEW_ABOUT = 'bla bla bla'
        NEW_FN = 'Юля'
        response = self.client.put(
            reverse('user-detail', kwargs={'pk': self.test_user.pk}),
            json.dumps({
                'about': NEW_ABOUT,
                'first_name': NEW_FN,
                'gender': FEMALE,
                'birth_date': DEFAULT_BIRTH_DATE.isoformat()
            }),
            content_type='application/json',
        )

        fields = ('id', 'first_name', 'about', 'gender', 'birth_date')
        data = response.data
        check_json(data, fields)
        self.assertEqual(response.data['first_name'], NEW_FN)
        self.assertEqual(response.data['about'], NEW_ABOUT)

    def test_update_another(self):
        NEW_ABOUT = 'bla bla bla'
        NEW_FN = 'Юля'
        who_trying_to_update = client_creation("kek", "lol")

        response = who_trying_to_update.put(
            reverse('user-detail', kwargs={'pk': self.test_user.pk}),
            json.dumps({
                'about': NEW_ABOUT,
                'first_name': NEW_FN,
                'gender': FEMALE,
                'birth_date': DEFAULT_BIRTH_DATE.isoformat()
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_update_meeting(self):
        response = self.client.put(
            reverse('meeting-detail', kwargs={'pk': self.test_meeting_1.pk}),
            json.dumps({
                'title': self.NEW_MEET_TITLE,
                'description': self.NEW_MEET_DESC,
                'coordinates': self.coords,
                'meeting_date': MEETING_DATE_1.strftime("%Y-%m-%d"),
                'group_type': GROUP_MEETING
            }),
            content_type='application/json'
        )

        data = response.data
        fields = ('id', 'title', 'description', 'coordinates', 'owner', 'meeting_date', 'group_type')
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
                'coordinates': self.coords,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_wrong_user(self):
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


class ConfirmCases(ConfirmMixin, MeetingMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.meeting_creator = client_creation('creator', 'lol')
        self.meeting_id = self.create_meeting(1, 1, 'keklol', self.meeting_creator).data['id']
        self.fst_successor = client_creation('fst_successor', 'lol')
        self.snd_successor = client_creation('snd_successor', 'lol')
        # 1st and 2nd clients trying to participate
        self.fst_successor.post(reverse('meeting-confirm', kwargs={'pk': self.meeting_id}))
        self.snd_successor.post(reverse('meeting-confirm', kwargs={'pk': self.meeting_id}))

    def test_list_confirms(self):
        creator_confirmations_r = self.meeting_creator.get(reverse('confirms-list'))
        fields = ('id', 'title', 'description', 'owner', 'subway', 'group_type')
        fst_meeting = creator_confirmations_r.data[0]['meeting']
        snd_meeting = creator_confirmations_r.data[1]['meeting']
        confims_frombase = Confirm.objects.all().filter(meeting__owner__username='creator')
        for item in confims_frombase:
            self.assertTrue(item.is_read)
        check_json(fst_meeting, fields)
        check_json(snd_meeting, fields)
        self.assertEqual(fst_meeting['color_status'], MINE)
        self.assertEqual(snd_meeting['color_status'], MINE)

    def test_proper_color_serialization(self):
        confirmed_conf = Confirm.objects.all().filter(user__username='fst_successor')
        response = self.meeting_creator.put(
            reverse('confirm-action', kwargs={'pk': confirmed_conf[0].id}),
            json.dumps({
                'is_approved': True,
                'is_read': True
            }),
            content_type='application/json',
        )
        Confirm.objects.all().filter(
            user__username='fst_successor', meeting=confirmed_conf[0].meeting, is_approved=True)
        meetings = self.fst_successor.get(reverse('meetings-list') + "?lng={0}&lat={1}&r={2}".format(1, 1, 10))

        data = meetings.data
        self.assertEqual(data[0]['color_status'], APPROVED)
        meetings = self.snd_successor.get(reverse('meetings-list') + "?lng={0}&lat={1}&r={2}".format(1, 1, 10))
        data = meetings.data
        self.assertEqual(data[0]['color_status'], DISAPPROVED)

    def test_approve__success(self):
        self.assertFalse(self.test_confirm.is_approved)
        response = self.client.put(
            reverse('confirm-action', kwargs={'pk': self.test_confirm.pk}),
            json.dumps({
                'is_approved': True,
                'is_read': True
            }),
            content_type='application/json',
        )
        code = response.status_code
        self.assertEqual(code, 200)
        confirm = Confirm.objects.get(pk=self.test_confirm.pk)
        self.assertTrue(confirm.is_approved)
        self.assertTrue(confirm.is_read)

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
        self.assertFalse(confirm.is_read)

    def test_try_confir_twise(self):
        response = self.client.post(reverse('meeting-confirm', kwargs={'pk': self.test_meeting_1.id}))
        self.assertEqual(response.data['status'], 400)

    def test_count_confirms(self):
        resp = self.meeting_creator.get(reverse('unread-confirms'))
        data = resp.data['data']
        self.assertEqual(data['unread'], 2)


class MeetingTypesTest(ConfirmMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_all_types(self):
        check = self.client.get(reverse('meeting-types'))
        types = [["general", 0], ["sport", 1], ["bar", 2], ["dance", 3]]
        data = check.data['data']
        data = json.loads(data)
        for tup in data:
            self.assertTrue(tup in types)


class UploadDeletePhotoTest(AuthUserMixin, TestCase):
    def create_photo(self, file_name):
        image = Image.new('RGBA', size=(50, 50), color=(150, 150, 0))
        image.save(file_name)

        response = self.client.put(
            reverse('upload-photo', kwargs={'filename': file_name}),
            data=image,
            content_type='image/jpeg'
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
        self.create_photo(file_name)
        photos = UserPhotos.objects.all()
        kek_id = photos[0].id
        response = self.client.delete(reverse('delete-photo', kwargs={'pk': kek_id}))
        data = response.data
        self.assertEqual(data['status'], 204)
        os.remove(file_name)
