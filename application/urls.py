from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # create user curl --data "username=<uname>&password=<pw>" http://site-name/api-token-auth/
    url(r'^api-token-auth/', obtain_auth_token)
)
