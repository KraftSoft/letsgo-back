from rest_framework import serializers

from chat.models import Message, Chat
from core.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Message
        fields = ('text', 'author', 'is_read', 'is_received', 'date_create')


class ChatSerializer(serializers.ModelSerializer):

    owner = UserSerializer()
    users = UserSerializer(many=True)
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(chat_id=obj.id).order_by('id').last()
        return MessageSerializer(last_msg).data

    class Meta:
        model = Chat
        fields = ('title', 'owner', 'users', 'channel_slug', 'last_message')
