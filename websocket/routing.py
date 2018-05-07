from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/chat/<room_id>/', consumers.ChatConsumer),
    path('ws/notice/<user_id>/', consumers.NoticeConsumer)
]