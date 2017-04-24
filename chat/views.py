from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Message, Chat
from core.utils import JsonResponse
from core.serializers import JsonResponseSerializer as JRS


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
