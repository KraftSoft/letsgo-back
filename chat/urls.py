from django.conf.urls import url

from chat.views import SaveMessage

urlpatterns = [
    url(r'^save_message/', SaveMessage.as_view(), name='save_message'),
]
