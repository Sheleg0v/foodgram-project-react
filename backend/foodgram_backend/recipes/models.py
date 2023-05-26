import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Name'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Color'
    )
    slug = models.SlugField(
        max_length=30,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', self.color):
            raise ValidationError(
                'Invalid color format. Please use a valid hex color.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.TextField(
        max_length=100,
        verbose_name='Name'
    )
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name='Measurement unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        blank=True,
        verbose_name='Tags'
    )
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты'
    )
    name = models.CharField(
        max_length=30,
        verbose_name='Name'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Image'
    )
    text = models.TextField('Text')
    cooking_time = models.PositiveSmallIntegerField('Cooking time')
    pub_date = models.DateTimeField('Publication date', auto_now_add=True)

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_recipe_tag'
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField('Amount')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class RecipeUser(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_user'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_favorited = models.BooleanField(
        default=False, verbose_name='In favotite'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False, verbose_name='In shopping cart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_recipe_user'
            )
        ]
