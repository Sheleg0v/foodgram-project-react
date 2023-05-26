import django_filters.rest_framework as filters

from recipes.models import Ingredient, Recipe, RecipeUser


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author')

    def filter_tags(self, queryset, name, value):
        tags = self.data._getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_is_favorited(self, queryset, name, value):
        if self.data.get('is_favorited') != '1':
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        recipe_user_objects = RecipeUser.objects.filter(
            user=user, is_favorited=True
        )
        recipes_id = []
        for recipe_user_object in recipe_user_objects:
            recipes_id.append(recipe_user_object.recipe.id)
        return Recipe.objects.filter(id__in=recipes_id)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.data.get('is_in_shopping_cart') != '1':
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        recipe_user_objects = RecipeUser.objects.filter(
            user=user, is_in_shopping_cart=True
        )
        recipes_id = []
        for recipe_user_object in recipe_user_objects:
            recipes_id.append(recipe_user_object.recipe.id)
        return Recipe.objects.filter(id__in=recipes_id)
