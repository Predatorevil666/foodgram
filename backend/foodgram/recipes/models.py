from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.crypto import get_random_string

from recipes.constants import USER_LENGTH

User = get_user_model()


class Tag(models.Model):
    """Модель для описания тега."""

    name = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Название',
        blank=False,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите цвет в формате HEX ('
                        'например, #ffffff или #fff).'
            )
        ],
        default="#ffffff",
        help_text='Введите цвет тега. Например, #ffffff',
    )
    slug = models.SlugField(
        max_length=USER_LENGTH,
        verbose_name='Уникальный слаг',
        blank=False,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    """Модель для описания ингредиента."""

    name = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для описания рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(

        max_length=USER_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Фотография рецепта',
        upload_to='recipes/',
    )
    text = models.CharField(
        max_length=1500,
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,

        verbose_name='Ингредиенты',
        through='IngredientInRecipe',
        related_name='recipes',

    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    slug = models.SlugField(unique=True, default=get_random_string(6))

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:100]


class IngredientInRecipe(models.Model):
    """Модель для описания количества ингредиентов в отдельных рецептах."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_list",
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!')
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients_in_the_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для описания формирования покупок. """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Добавил в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart'
        )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    """Модель для добавления рецептов в  избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Добавил в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
