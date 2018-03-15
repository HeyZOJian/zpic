from django.urls import path, include
from .views import *

urlpatterns = [
    path('upload/', upload_image),
    path('<int:pk>/', get_image_detail),
    path('<int:pk>/comments/', comment_image),
    path('<int:pk>/likes/', like_image),
    path('<int:pk>/unlikes/', unlike_image),
    path('<int:pk>/views/', view_image),
]