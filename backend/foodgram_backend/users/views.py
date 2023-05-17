from django.shortcuts import get_object_or_404
from rest_framework import decorators, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import User
from .serializers import (ChangePasswordSerializer, TokenSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        else:
            return [permissions.AllowAny()]


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
        {'detail': 'Password changed successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
