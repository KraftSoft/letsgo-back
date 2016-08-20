from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.test import Client
from core.models import User
from core.serializers import UserSerializer
from rest_framework.authtoken.models import Token

TEST_USER_1 = 'masha'
TEST_USER_PW_1 = '0'

TEST_USER_2 = 'katya'
TEST_USER_PW_2 = '0'


def check_json(data, fields):
    for field in fields:
        assert field in data, 'Field "{}" is not returned in response\nResponse data: {}'.format(field, data)


class AuthUserMixin(object):
    def setUp(self):
        self.test_user = User.objects.create(username=TEST_USER_1)
        self.test_user.set_password(TEST_USER_PW_1)
        self.test_user.save()
        self.token, _ = Token.objects.get_or_create(user=self.test_user)
        self.token = self.token.key


class CoreTests(AuthUserMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_auth_user(self):
        response = self.client.post(reverse('auth'), {'username': TEST_USER_1, 'password': TEST_USER_PW_1})
        fields = ('token',)
        check_json(response.data, fields)
        self.assertEqual(response.data['token'], self.token)

    def test_create_user(self):
        response = self.client.post(reverse('user-create'), {'username': TEST_USER_2, 'password': TEST_USER_PW_2},
                                    Authorization=self.token)
        fields = ('id', 'username')
        check_json(response.data, fields)

    def test_get_user(self):
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.test_user.pk}), Authorization=self.token)
        fields = ('id', 'first_name', 'about', 'username')
        check_json(response.data, fields)


class UpdateCases(AuthUserMixin, TransactionTestCase):
    NEW_USER_NAME = 'july'
    NEW_ABOUT = 'bla bla bla'
    NEW_FN = 'Юля'

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_update_user(self):
        import json
        response = self.client.put(
            reverse('user-detail', kwargs={'pk': self.test_user.pk}),
            json.dumps({
                'username': self.NEW_USER_NAME,
                'about': self.NEW_ABOUT,
                'first_name': self.NEW_FN
            }),
            content_type='application/json',
            Authorization=self.token,
        )

        fields = ('id', 'first_name', 'about', 'username')

        check_json(response.data, fields)

        self.assertEqual(response.data['username'], self.NEW_USER_NAME)
        self.assertEqual(response.data['first_name'], self.NEW_FN)
        self.assertEqual(response.data['about'], self.NEW_ABOUT)
