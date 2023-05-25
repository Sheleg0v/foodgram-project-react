import base64

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers, validators

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeUser,
    Tag
)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgage_string = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgage_string), name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


class RecipeBaseSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeWriteSerializer(RecipeBaseSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = serializers.ListField(child=serializers.DictField())
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(RecipeBaseSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipeingredient_set.all'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        try:
            return obj.recipe_user.get(user=user).is_favorited
        except RecipeUser.DoesNotExist:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        try:
            return obj.recipe_user.get(user=user).is_in_shopping_cart
        except RecipeUser.DoesNotExist:
            return False


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
        serializer = ShortRecipeSerializer(
            recipe_obj, many=True, context=self.context
        )
        return serializer.data


class IsFavoritedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeUser
        fields = ('recipe', 'user', 'is_favorited')
        read_only_fields = ('recipe', 'user', 'is_favorited')

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(instance.recipe)
        return serializer.data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = RecipeUser.objects.get_or_create(user=user, recipe=recipe)[0]
        if obj.is_favorited is True:
            raise exceptions.ValidationError(
                "This recipe is already in favorite"
            )
        obj.is_favorited = True
        obj.save()
        return obj


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IsInShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeUser
        fields = ('recipe', 'user', 'is_in_shopping_cart')
        read_only_fields = ('recipe', 'user', 'is_in_shopping_cart')

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(instance.recipe)
        return serializer.data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = RecipeUser.objects.get_or_create(user=user, recipe=recipe)[0]
        if obj.is_in_shopping_cart is True:
            raise exceptions.ValidationError(
                "This recipe is already in shopping cart"
            )
        obj.is_in_shopping_cart = True
        obj.save()
        return obj
