from django.conf.urls import url

from chat.views import SaveMessage, ChatsList, MessageList

urlpatterns = [
    url(r'^save_message/', SaveMessage.as_view(), name='save_message'),
    url(r'^chats-list/', ChatsList.as_view(), name='chats-list'),
    url(r'^message-list/(?P<chat_pk>\d+)/', MessageList.as_view(), name='chats-list')
]
