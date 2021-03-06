from django.conf.urls import url

from core.views import UserList, UserDetail, MeetingsList, MeetingDetail, AuthView, FileUploadView, SetAvatar, \
    ConfirmCreate, ConfirmsList, AcceptConfirm, DeletePhoto, MeetingTypes, UnreadConfirms, UpdateClientKey

urlpatterns = [

    url(r'^api-token-auth/', AuthView.as_view(), name='auth'),
    url(r'^users-list/$', UserList.as_view(), name='users-list'),

    url(r'^user-detail/$', UserDetail.as_view(), name='user-detail'),
    url(r'^user-detail/(?P<pk>\d+)/$', UserDetail.as_view(), name='user-detail'),

    url(r'^meetings-list/$', MeetingsList.as_view(), name='meetings-list'),

    url(r'^meeting-detail/$', MeetingDetail.as_view(), name='meeting-detail'),
    url(r'^meeting-detail/(?P<pk>\d+)/$', MeetingDetail.as_view(), name='meeting-detail'),

    url(r'^upload-photo/(?P<filename>[^/]+)$', FileUploadView.as_view(), name='upload-photo'),

    url(r'^delete-photo/(?P<pk>\d+)/$', DeletePhoto.as_view(), name='delete-photo'),

    url(r'^set-avatar/(?P<pk>\d+)/$', SetAvatar.as_view(), name='set-avatar'),

    url(r'^meeting-confirm/(?P<pk>\d+)/$', ConfirmCreate.as_view(), name='meeting-confirm'),

    url(r'^confirms-list/$', ConfirmsList.as_view(), name='confirms-list'),

    url(r'^confirm-action/(?P<pk>\d+)/$', AcceptConfirm.as_view(), name='confirm-action'),

    url(r'^meeting-types/$', MeetingTypes.as_view(), name='meeting-types'),

    url(r'^unread-confirms/$', UnreadConfirms.as_view(), name='unread-confirms'),

    url(r'^set-client-key/$', UpdateClientKey.as_view(), name='set-client-key'),

]

