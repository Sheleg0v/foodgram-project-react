from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=30,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField(
        max_length=100,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name='Еденицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        blank=True,
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты'
    )
    name = models.CharField(
        max_length=30,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    text = models.TextField('Текст')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
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
    amount = models.PositiveSmallIntegerField('Количество')

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
        default=False, verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False, verbose_name='В корзине'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_recipe_user'
            )
        ]
