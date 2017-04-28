from chat.models import Chat, Message
from chat.serializers import ChatSerializer, MessageSerializer


class ChatMixin(object):
    model = Chat
    serializer_class = ChatSerializer


class MessageMixin(object):
    model = Message
    serializer_class = MessageSerializer
