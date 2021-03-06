import json
import logging

import tornadoredis
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from tornado import websocket
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.web import Application
from tornadoredis.pubsub import BaseSubscriber
import redis

from chat.models import Chat
from core.models import User
from core.serializers import UserSerializer
from core.utils import build_absolute_url, reverse_full

logger = logging.getLogger(__name__)

r = redis.Redis(db=1)


class SubscribeManager(BaseSubscriber):
    def on_message(self, msg):
        if not msg:
            return
        if msg.kind == 'message' and msg.body:
            # Get the list of subscribers for this channel
            subscribers = list(self.subscribers[msg.channel].keys())

            message = json.loads(msg.body)

            if subscribers:
                for s in subscribers:
                    if r.get(s.session_key):
                        data = {
                            'text': message['text'],
                            'author_name': s.user.first_name,
                            'avatar': s.user.get_avatar(),
                            'href': reverse_full('user-detail', kwargs={'pk': s.user.id}),
                            'is_my': message['user']['id'] == s.user.id
                        }
                        s.write_message(json.dumps(data, ensure_ascii=False))
                    else:
                        # TODO SEND PUSH
                        pass

        super(SubscribeManager, self).on_message(msg)

publisher = SubscribeManager(tornadoredis.Client())
subscriber = SubscribeManager(tornadoredis.Client())


class ChatSocketHandler(websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_name = ''  # Chat unique slug
        self.session_key = None
        self.user = None

    def get_current_user(self):
        token = self.get_argument('token')
        try:
            return User.objects.get(auth_token__key=token)
        except User.DoesNotExist:
            return None

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):

        self.user = self.get_current_user()

        if not self.user:
            self.close()
            return

        self.session_key = 'user-{0}'.format(self.user.id)
        r.set(self.session_key, 1)

        self.channel_name = kwargs.get('channel')

        if not self.channel_name:
            self.close()
            return

        try:
            chat = Chat.objects.get(channel_slug=self.channel_name)
        except Chat.DoesNotExist:
            logger.exception('slug: {0}'.format(self.channel_name))
            self.close()
            return

        if not self.user == chat.owner and not chat.users.filter(id=self.user.id).exists():
            logger.warning('Someone try to connect to private chat. User_id: {0}'.format(self.user.id))
            self.close()
            return

        subscriber.subscribe(self.channel_name, self)

    def on_message(self, message):
        self.message = message
        data = {
            'text': message,
            'user': UserSerializer(self.user).data
        }
        publisher.publish(self.channel_name, data, callback=self.new_message_callback)

    def new_message_callback(self, result):

        if result:

            http_client = AsyncHTTPClient()
            url = build_absolute_url('{0}'.format(reverse('save_message')))

            request = HTTPRequest(
                url,
                method="POST",
                body=urlencode({
                    "message": self.message.encode("utf-8"),
                    "api_key": settings.CHAT_API_KEY,
                    "sender_id": self.user.id,
                    "chat_slug": self.channel_name,
                }),
                headers={
                    'Authorization': 'Token {0}'.format(self.user.auth_token.key)
                }
            )
            http_client.fetch(request, self.handle_request)

    def data_received(self, chunk):
        pass

    def handle_request(self, *args, **kwargs):
        pass

    def on_close(self):
        if self.session_key:
            r.delete(self.session_key)

    def __del__(self):
        if self.session_key and r.get(self.session_key):
            r.delete(self.session_key)

application = Application([
    ('/chat/(?P<channel>\w+)/', ChatSocketHandler),
])
