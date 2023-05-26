from django.contrib import admin
from django.db.models import Count, Q

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    RecipeUser,
    Tag
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorite_count')
    list_filter = ('author', 'name', 'tags')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count(
            'recipe_user', filter=Q(recipe_user__is_favorited=True)
        ))
        return queryset

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = 'In favorite, times'


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient')


class RecipeUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeUser, RecipeUserAdmin)
