from django.urls import path, include
from .views import *

urlpatterns = [
    path('upload/', upload_image),
    path('comments/<int:pk>/', comment_image),
    path('likes/<int:pk>/', like_image),
    path('<int:pk>/', get_image_detail),
    path('view/<int:pk>/', get_image_views),
    path('like/<int:pk>/', get_image_likes),
    path('hots/week/<int:page>/', get_hots_week),
]