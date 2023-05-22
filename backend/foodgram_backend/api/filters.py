import django_filters.rest_framework as filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    is_favorited = filters.BooleanFilter(
        field_name='recipe_user__is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='recipe_user__is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author')

    def filter_tags(self, queryset, name, value):
        tags = self.data._getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()
