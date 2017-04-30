from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from chat.models import Message, Chat
from core.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    is_my = SerializerMethodField()

    def get_is_my(self, obj):
        return self.context['view'].request.user == obj.author

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
        fields = ('id', 'title', 'owner', 'users', 'channel_slug', 'last_message')
