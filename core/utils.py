from django.conf import settings
from django.core.urlresolvers import reverse


class JsonResponse(object):
    def __init__(self, status, msg, data=None):
        self.status = status
        self.msg = msg
        self.data = data


def reverse_full(slug, *args, **kwargs):

    path = reverse(slug, *args, **kwargs)
    return build_absolute_url(path)


def build_absolute_url(path):
    return '{}://{}{}'.format(settings.BASE_SCHEMA, settings.BASE_DOMAIN, path)
