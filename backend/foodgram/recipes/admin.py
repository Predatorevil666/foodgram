from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)


class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для управления ингредиентами."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = 'Новый ингредиент'


class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админ-панель для управления ингредиентами в рецептах."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


class TagAdmin(admin.ModelAdmin):
    """Админ-панель для управления тегами."""

    list_display = ('name', 'color', 'slug')
    list_editable = ('color',)
    empty_value_display = 'Новый таг'


class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для управления рецептами."""

    list_display = ('name', 'author', 'pub_date', 'favorite_count')
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    ordering = ('-pub_date',)
    empty_value_display = 'Новый рецепт'

    def favorite_count(self, obj):
        """Метод для подсчета количества добавлений в избранное."""
        return Favorite.objects.filter(recipe=obj).count()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'author').prefetch_related('ingredients', 'tags')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'recipe')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
