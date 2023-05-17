from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        model = User
        validators = [
            validators.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return obj.subscribers.filter(id=user.id).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        if self.context['request'].method == 'POST':
            data.pop('is_subscribed')
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data.get('password')
            )
        return super().update(instance, validated_data)


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=settings.EMAIL_CHAR_LENGTH
    )
    password = serializers.CharField(
        max_length=settings.PASSWORD_LENGTH
    )

    def validate(self, data):
        user = get_object_or_404(
            User,
            email=data['email']
        )
        if not check_password(data['password'], user.password):
            raise serializers.ValidationError('Неверный email или пароль!')
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128, write_only=True)
    current_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        request = self.context.get('request')
        user = authenticate(
            request=request,
            username=request.user.username,
            password=data['current_password']
        )
        if not user:
            raise serializers.ValidationError('Invalid current password.')
        return data
