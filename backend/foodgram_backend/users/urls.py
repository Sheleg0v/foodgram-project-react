from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, change_password, delete_token, get_token,
                    user_me)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('users/me/', user_me),
    path('users/set_password/', change_password),
    path('', include(router.urls)),
    path('auth/token/login/', get_token),
    path('auth/token/logout/', delete_token),
]
