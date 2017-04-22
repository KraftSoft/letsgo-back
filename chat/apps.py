from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'chat'
    verbose_name = "Chat"

    def ready(self):
        from chat.signals.handlers import add_to_chat #noqa