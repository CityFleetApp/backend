from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^new/$', views.new_room, name='new_room'),
    url(r'^(?P<label>[\d]+)/$', views.chat_room, name='chat_room'),
]
