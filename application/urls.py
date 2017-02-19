from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.conf import settings

from core.views import OAuth

admin.autodiscover()

urlpatterns = [
    url(r'^', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social_django.urls', namespace='social')),
    url(r'^{0}'.format(settings.SOCIAL_AUTH_LOGIN_URL), OAuth.as_view()),
    url(r'^api-token-auth/', obtain_auth_token)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
