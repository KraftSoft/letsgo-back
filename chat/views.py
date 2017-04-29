from django.conf import settings
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.mixins import ChatMixin, MessageMixin
from chat.models import Message, Chat
from core.utils import JsonResponse
from core.serializers import JsonResponseSerializer as JRS


class ChatsList(ChatMixin, ListAPIView):
    def get(self, request, *args, **kwargs):
        self.queryset = (
            Chat.
            objects.
            select_related('owner').
            prefetch_related('users').
            filter(Q(owner=request.user) | Q(users__in=[request.user])).
            order_by('-id')
        )
        return super().get(request, *args, **kwargs)


class MessageList(MessageMixin, ListAPIView):
    def get(self, request, *args, **kwargs):

        chat_pk = kwargs['chat_pk']
        try:
            chat = Chat.objects.get(pk=chat_pk)
        except Chat.DoesNotExist:
            return Response(JRS(JsonResponse(
                status=404, msg='chat does not exist')).data)

        if Chat.objects.filter(Q(users__in=[self.request.user]) | Q(owner=self.request.user)).exists():
            self.queryset = Message.objects.select_related('author').filter(chat=chat).order_by('id')
            return super().get(request, *args, **kwargs)

        return Response(JRS(JsonResponse(
            status=400, msg='you can not see this chat')).data)


class SaveMessage(APIView):

    def post(self, request, *args, **kwargs):

        key = request.POST.get('api_key')
        message = request.POST.get('message')
        chat_slug = request.POST.get('chat_slug')

        if key != settings.CHAT_API_KEY:
            return Response(JRS(JsonResponse(
                    status=400, msg='wrong key')).data)

        try:
            chat = Chat.objects.get(channel_slug=chat_slug)
        except Chat.DoesNotExist:
            return Response(JRS(JsonResponse(
                status=400, msg='chat does not exist')).data)

        Message.objects.create(
            chat=chat,
            author=request.user,
            text=message
        )

        return Response(JRS(JsonResponse(status=200, msg='ok')).data)
