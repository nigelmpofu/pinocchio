from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from peer_review import views

urlpatterns = [
                  url(r'^admin/', include(admin.site.urls)),
                  url(r'^fileUpload', views.fileUpload, name='fileUpload'),
                  url(r'^questionAdmin', views.questionAdmin, name='questionAdmin'),
                  url(r'^createQuestion/$', views.createQuestion, name='createQuestion'),
                  url(r'^maintainRound/$', views.maintainRound, name='maintainRound'),
                  url(r'^maintainTeam/$', views.maintainTeam, name='maintainTeam'),

                  url(r'^$', views.index, name='index'),
                  url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
                  url(r'^userAdmin/submitForm/?$', views.submitForm),
                  url(r'^userAdmin/submitCSV/$', views.submitCSV, name="submitCSV"),
                  url(r'^userAdmin/delete/(?P<userPk>[0-9]+)/?$', views.userDelete),
                  url(r'^userAdmin/update/(?P<userPk>[0-9]+)/?$', views.userUpdate),
                  url(r'^userAdmin/$', views.userList),
                  url(r'^questionList/$', views.questionList),
                  url(r'^questionList/delete/(?P<questionPk>[0-9]+)/?$', views.questionDelete),
                  url(r'^questionList/update/(?P<questionPk>[0-9]+)/?$', views.questionUpdate),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
