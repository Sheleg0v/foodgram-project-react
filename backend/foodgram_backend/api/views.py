from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, RecipeUser, Tag
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    status,
    viewsets
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor
from .serializers import (
    IngredientSerializer,
    IsFavoritedSerializer,
    IsInShoppingCartSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)
from core.pagination import PageLimitPagination


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageLimitPagination
    filterset_class = RecipeFilter
    ordering_fields = ('-pub_date',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        return (IsAuthor(),)


class IsFavoritedViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RecipeUser.objects.all()
    serializer_class = IsFavoritedSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_destroy(self, instance):
        if instance.is_favorited is False:
            raise exceptions.ValidationError("This recipe is not in favorite")
        instance.is_favorited = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        try:
            instance = RecipeUser.objects.get(recipe=recipe, user=user)
        except RecipeUser.DoesNotExist:
            raise exceptions.ValidationError("This recipe is not in favorite")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsInShoppingCartViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RecipeUser.objects.all()
    serializer_class = IsInShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_destroy(self, instance):
        if not instance.is_in_shopping_cart:
            raise exceptions.ValidationError(
                "This recipe is not in shopping cart"
            )
        instance.is_in_shopping_cart = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        try:
            instance = RecipeUser.objects.get(recipe=recipe, user=user)
        except RecipeUser.DoesNotExist:
            raise exceptions.ValidationError(
                "This recipe is not in shopping cart"
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


def form_list(ingredient_total):
    return "\n".join([
        f"{ingredient['recipe__ingredients__name']} - "
        f"{ingredient['total_amount']} "
        f"{ingredient['recipe__ingredients__measurement_unit']}"
        for ingredient in ingredient_total
    ])


@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def download_shopping_cart_view(request):
    user = request.user
    shopping_cart = RecipeUser.objects.filter(
        user=user, is_in_shopping_cart=True
    )

    ingredient_total = shopping_cart.values(
        'recipe__ingredients__name', 'recipe__ingredients__measurement_unit'
    ).annotate(total_amount=Sum('recipe__recipeingredient__amount'))

    content = form_list(ingredient_total)

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
    )

    return response
