from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
    MultipleChoiceFilter
)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр для модели ингредиентов."""

    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для модели рецептов."""

    author = NumberFilter(field_name='author__id')
    tags = CharFilter(field_name='tags__slug', method='filter_by_tags')
    is_favorited = BooleanFilter(method='filter_favorites')
    is_in_shopping_cart = BooleanFilter(field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorites(self, queryset, name, value):
        """Фильтрация рецептов по избранному."""
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_by_tags(self, queryset, name, value):
        """Фильтрация рецептов по тегам."""
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()
