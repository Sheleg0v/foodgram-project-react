import base64

from core.serializers import ShortRecipeSerializer
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Ingredient, Recipe, RecipeIngredient, RecipeUser,
                            Tag)
from rest_framework import exceptions, serializers

from users.serializers import UserSerializer


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
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
            ingredient = Ingredient.objects.get(id=ingredient_id)
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
