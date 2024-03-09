from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.CustomUserView, basename='customuser')
router.register(r'tasks', views.TaskView)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'tasks/<int:pk>/add_team_member/',
        views.TaskView.as_view({'patch': 'add_team_member'}),
        name='task-add_team_member'
    ),
    path(
        'tasks/<int:pk>/remove_team_member/',
        views.TaskView.as_view({'delete': 'remove_team_member'}),
        name='task-remove_team_member'
    ),
]
