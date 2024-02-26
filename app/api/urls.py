from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('user', views.UserView)


urlpatterns = [
    path('', include(router.urls))
]
