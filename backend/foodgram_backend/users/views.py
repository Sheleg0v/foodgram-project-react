from django.shortcuts import get_object_or_404
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    status,
    viewsets
)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import (
    ChangePasswordSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TokenSerializer,
    UserSerializer
)
from core.pagination import PageLimitPagination


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination


@decorators.api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        email=serializer.validated_data['email']
    )
    token, created = Token.objects.get_or_create(user=user)
    return Response({'auth_token': token.key}, status=status.HTTP_201_CREATED)


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def delete_token(request):
    user = request.user
    get_object_or_404(Token, user=user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def user_me(request):
    user = request.user
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    return Response(
        {'detail': 'Пароль успешно изменен.'},
        status=status.HTTP_204_NO_CONTENT
    )


class SubscribeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if author == self.request.user:
            raise exceptions.ValidationError("You can't subscribe to yourself")
        if Subscription.objects.filter(
            author=author, subscriber=self.request.user
        ):
            raise exceptions.ValidationError('You already subscribed')
        serializer.save(author=author, subscriber=self.request.user)

    def get_object(self):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if not Subscription.objects.filter(
            author=author, subscriber=self.request.user
        ):
            raise exceptions.ValidationError('You are not subscribed')
        return Subscription.objects.get(
            author=author, subscriber=self.request.user
        )


class SubscriptionViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    pagination_class = PageLimitPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
