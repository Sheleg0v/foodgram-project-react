from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from .models import Subscription, User


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
        request = self.context.get('request')
        if request and request.method == 'POST':
            data.pop('is_subscribed')
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super().create(validated_data)


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
        if not check_password(data.get('password'), user.password):
            raise serializers.ValidationError('Неверный email или пароль!')
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=settings.PASSWORD_LENGTH, write_only=True
    )
    current_password = serializers.CharField(
        max_length=settings.PASSWORD_LENGTH, write_only=True
    )

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


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')
        read_only_fields = ('author', 'subscriber')

    def to_representation(self, instance):
        return SubscriptionSerializer(instance, context=self.context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipe.count')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        if obj:
            return True

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        recipe_obj = obj.author.recipe.all()
        if limit:
            recipe_obj = recipe_obj[:int(limit)]
        from api.serializers import ShortRecipeSerializer
        serializer = ShortRecipeSerializer(
            recipe_obj, many=True, context=self.context
        )
        return serializer.data
