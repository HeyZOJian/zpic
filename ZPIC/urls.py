"""ZPIC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from account.urls import urlpatterns as account_urls
from image.urls import urlpatterns as image_urls
from account.views import user_index, moments
from image.views import hots_day, hots_week, hots_month

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(account_urls)),
    path('moments/', moments),
    path('p/', include(image_urls)),
    path('<nickname>/', user_index),
    path('hots/day/', hots_day),
    path('hots/week/', hots_week),
    path('hots/month/', hots_month),
]
