from django.conf.urls import url

from core.views import UserList, UserDetail, MeetingsList, MeetingDetail, UserCreate, AuthView, FileUploadView, IndexView, SetAvatar

urlpatterns = [

    url(r'^api-token-auth/', AuthView.as_view(), name='auth'),
    url(r'^user-create/$', UserCreate.as_view(), name='user-create'),
    url(r'^users-list/$', UserList.as_view(), name='users-list'),

    url(r'^user-detail/$', UserDetail.as_view(), name='user-detail'),
    url(r'^user-detail/(?P<pk>\d+)/$', UserDetail.as_view(), name='user-detail'),

    url(r'^meetings-list/$', MeetingsList.as_view(), name='meetings-list'),

    url(r'^meeting-detail/$', MeetingDetail.as_view(), name='meeting-detail'),
    url(r'^meeting-detail/(?P<pk>\d+)/$', MeetingDetail.as_view(), name='meeting-detail'),

    url(r'^upload-photo/(?P<filename>[^/]+)$', FileUploadView.as_view(), name='upload-photo'),
    url(r'^index$', IndexView.as_view(), name='core-index'),
    url(r'^set-avatar/(?P<pk>\d+)/$', SetAvatar.as_view(), name='set-avatar'),
]
