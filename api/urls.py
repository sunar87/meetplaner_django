from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, EventViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
