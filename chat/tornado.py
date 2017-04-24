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
from core.utils import build_absolute_url

logger = logging.getLogger(__name__)

r = redis.Redis(db=1)


class SubscribeManager(BaseSubscriber):
    def on_message(self, msg):
        if not msg:
            return
        if msg.kind == 'message' and msg.body:
            # Get the list of subscribers for this channel
            subscribers = list(self.subscribers[msg.channel].keys())
            if subscribers:
                # Use the first active subscriber/client connection
                # for broadcasting. Thanks to Jonas Hagstedt
                for s in subscribers:
                    if r.get(s.session_key):
                        s.write_message(msg.body)
                        break
                    else:
                        # TODO SEND PUSH
                        pass

        super(SubscribeManager, self).on_message(msg)

publisher = SubscribeManager(tornadoredis.Client())


class AuthMixin(object):
    def get_user(self, token=None):

        if not token:
            header = self.request.headers.get('Authorization')
            if not header:
                return None

            try:
                token = header.split(' ')[1]
            except IndexError:
                logger.error('Invalid authorization header {0}'.format(header))
                return None

        try:
            return User.objects.get(auth_token__key=token)
        except User.DoesNotExist:
            logger.warning('Request with bad token {0}'.format(token))


class ChatSocketHandler(AuthMixin, websocket.WebSocketHandler):

    waiters = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_name = ''  # Chat unique slug

        self.subscriber = SubscribeManager(tornadoredis.Client())

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):

        token = kwargs.get('token')

        self.user = self.get_user(token)

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

        self.subscriber.subscribe(self.channel_name, self)

    def on_message(self, message):
        self.message = message
        publisher.publish(self.channel_name, message, callback=self.new_message_callback)

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
        r.delete(self.session_key)

    def __del__(self):
        if r.get(self.session_key):
            r.delete(self.session_key)

application = Application([
    ('chat/(?P<channel>\w+)/(?P<token>\w+)/', ChatSocketHandler),
])
