from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /myapp/
    url(r'^$', views.list, name='list'),

]