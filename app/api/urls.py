from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('create', views.UserCreateView.as_view(), name='create-user')
]
