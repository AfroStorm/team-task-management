from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.CustomUserView, basename='customuser')
router.register(r'tasks', views.CustomUserView, basename='task')

urlpatterns = [
    path('', include(router.urls))
]
