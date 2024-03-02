from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.CustomUserView, basename='customuser')

urlpatterns = [
    path('', include(router.urls))
]
