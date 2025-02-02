from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingCart, Tag
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = 'Новый ингредиент'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_editable = ('color',)
    empty_value_display = 'Новый таг'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    empty_value_display = 'Новый рецепт'

    def favorite_count(self, obj):
        """Метод для подсчета количества добавлений в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
