from django.urls import path,include
from .views import *
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

friendship_urls = [
    path('<int:pk>/follow/', follow_user),
    path('<int:pk>/unfollow/', unfollow_user)
]

urlpatterns = [
    path('register/', user_register),
    path('login/', user_login),
    path('logout/', user_logout),
    path('check_username/', check_username),
    path('check_nickname/', check_nickname),
    path('edit/', user_update),
    path('profile_photo/', change_profile_photo),
    path('friend/', include(friendship_urls)),
    path('search/', search_user),
    path('lock/', lock_account),
    path('unlock/', unlock_account)
]