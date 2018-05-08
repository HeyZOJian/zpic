from django.urls import path, include
from . import views

urlpatterns = [
    # path('', views.index, name = 'index'),
    # path('<room_id>/', views.room, name = 'room')
    path('notice/', views.notice),
]