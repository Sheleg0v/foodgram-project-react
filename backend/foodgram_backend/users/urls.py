from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    SubscribeViewSet,
    SubscriptionViewSet,
    UserViewSet,
    change_password,
    delete_token,
    get_token,
    user_me
)

router = DefaultRouter()
router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
router.register('users', UserViewSet, basename='users')


subscription_urls = SubscribeViewSet.as_view({
    'post': 'create',
    'delete': 'destroy'
})

urlpatterns = [
    path('users/me/', user_me),
    path('users/set_password/', change_password),
    path(
        'users/<int:id>/subscribe/',
        subscription_urls,
        name='subscription-detail'
    ),
    path('', include(router.urls)),
    path('auth/token/login/', get_token),
    path('auth/token/logout/', delete_token),
]
