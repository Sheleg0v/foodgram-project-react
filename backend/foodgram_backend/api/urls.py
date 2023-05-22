from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, IsFavoritedViewSet,
                    IsInShoppingCartViewSet, RecipeViewSet, TagViewSet,
                    download_shopping_cart_view)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingridients')
router.register('recipes', RecipeViewSet, basename='recipes')

is_favorited_urls = IsFavoritedViewSet.as_view({
    'post': 'create',
    'delete': 'destroy'
})
is_in_shopping_cart_urls = IsInShoppingCartViewSet.as_view({
    'post': 'create',
    'delete': 'destroy'
})

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        is_favorited_urls,
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        is_in_shopping_cart_urls,
        name='shopping_cart'
    ),
    path('recipes/download_shopping_cart/', download_shopping_cart_view),
    path('', include(router.urls)),
    path('', include('users.urls')),
]
