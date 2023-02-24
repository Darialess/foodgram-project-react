from django.core.validators import MinValueValidator
from django.db import models
from users.models import User
from django.db.models import UniqueConstraint


class Tag(models.Model):
    """ Модель для тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега')
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta():
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    """Модель для рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200, verbose_name='Название рецепта')

    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тег'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        'Image',
        upload_to='static/recipe/',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель для избранногою"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='is_favorites'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_favorite_unique'
            )
        ] 


class ShoppingCart(models.Model):
    """Модель для корзины покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_shoppingcart_unique'
            )
        ]


class IngredientRecipe(models.Model):
    """Модель для связи ингредиентов и их количества в рецепте"""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1, 'Количество не может быть меньше 1.'),
        ],
        verbose_name='Количество'
    )


class Meta:
    constraints = [
        UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='recipe_ingredient_unique'
        )
    ]
