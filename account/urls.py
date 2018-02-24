from django.urls import path,include
from .views import *
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

user_urls = [


]

friendship_urls = [
    path('<int:pk>/follow/', follow_user),
    path('<int:pk>/unfollow/', unfollow_user),
    path('followers/', user_followers),
    path('followings/', user_followings),
]

urlpatterns = [
    path('register/', user_register),
    path('login/', user_login),
    path('logout/', user_logout),
    path('update/', user_update),
    path('friendships/', include(friendship_urls)),
]