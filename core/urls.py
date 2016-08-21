from django.conf.urls import patterns, url

from core.views import UserList, UserDetail, MeetingsList, MeetingDetail, UserCreate, MeetingAddMember, Centrefugo, \
    AuthView

urlpatterns = patterns('',

    url(r'^api-token-auth/', AuthView.as_view(), name='auth'),
    url(r'user-create/$', UserCreate.as_view(), name='user-create'),
    url(r'users-list/$', UserList.as_view(), name='users-list'),

    url(r'user-detail$', UserDetail.as_view(), name='user-detail'),
    url(r'user-detail/(?P<pk>\d+)$', UserDetail.as_view(), name='user-detail'),

    url(r'meetings-list/$', MeetingsList.as_view(), name='meetings-list'),

    url(r'meeting-detail$', MeetingDetail.as_view(), name='meeting-detail'),
    url(r'meeting-detail/(?P<pk>\d+)/$', MeetingDetail.as_view(), name='meeting-detail'),

    url(r'meeting-add-me/(?P<pk>\d+)/$', MeetingAddMember.as_view(), name='add-member'),
    url(r'centrifugo/$', Centrefugo.as_view(), name='centrifugo'),

)
