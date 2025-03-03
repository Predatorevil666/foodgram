import uuid
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string
from recipes.constants import (GENERATE_LENGTH, INGREDIENT_LENGTH,
                               MAX_COOKING_TIME, MAX_INGREDIENT_AMOUNT,
                               MEASUREMENT_UNIT_LENGTH, MIN_COOKING_TIME,
                               MIN_INGREDIENT_AMOUNT, RECIPE_LENGTH,
                               RECIPE_NAME_LENGTH, SHORT_LINK, TAG_LENGTH,
                               TAG_NAME_LENGTH)

User = get_user_model()


class Tag(models.Model):
    """Модель для описания тега."""

    name = models.CharField(
        max_length=TAG_LENGTH,
        verbose_name='Название',
        unique=True,
    )

    slug = models.SlugField(
        max_length=TAG_LENGTH,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:TAG_NAME_LENGTH]


class Ingredient(models.Model):
    """Модель для описания ингредиента."""

    name = models.CharField(
        max_length=INGREDIENT_LENGTH,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        unique_together = (('name', 'measurement_unit'),)

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

        max_length=RECIPE_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Фотография рецепта',
        upload_to='recipes/',
    )
    text = models.TextField(
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
            MinValueValidator(
                MIN_COOKING_TIME,
                message='Минимальное значение 1!'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='Максимальное значение 300!'
            )
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    slug = models.SlugField(
        max_length=SHORT_LINK,
        unique=True,
        # default=get_random_string(GENERATE_LENGTH),
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:RECIPE_NAME_LENGTH]

    def save(self, *args, **kwargs):
        """Генерация уникального slug перед сохранением."""
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """Генерирует уникальный slug с проверкой в базе."""
        while True:
            slug = uuid.uuid4().hex[:GENERATE_LENGTH]
            if not Recipe.objects.filter(slug=slug).exists():
                return slug


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
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message='Минимальное значение 1!'
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message='Максимальное значение 100!'
            )
        ],
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


class BaseShopping(models.Model):
    """Абстрактная базовая модель для корзины и избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)s_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(BaseShopping):
    """Модель для описания формирования покупок."""

    class Meta(BaseShopping.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(BaseShopping):
    """Модель для добавления рецептов в избранное."""

    class Meta(BaseShopping.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
