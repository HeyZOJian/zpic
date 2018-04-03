from django.urls import path, include
from .views import *

urlpatterns = [
    path('upload/', upload_image),
    path('<int:pk>/', get_image_detail),
    path('<int:pk>/comments/', image_comment),
    path('<int:pk>/like/', like_image),
    path('<int:pk>/unlike/', unlike_image),
    path('<int:pk>/views/', view_image),
]