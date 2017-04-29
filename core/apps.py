from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from chat.signals.handlers import add_to_chat #noqa