from django.urls import path
from .views import *


urlpatterns = [
    path('upload/', upload_image),
    path('comments/<int:pk>/', comment_image),
    path('<int:pk>/', get_image_detail),
]