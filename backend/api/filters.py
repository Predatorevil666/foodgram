from django.db.models import Q
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet, NumberFilter)

from recipes.models import Ingredient, Recipe


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
    is_in_shopping_cart = BooleanFilter(
        method="filter_shopping_cart",
        field_name='shopping_recipe'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов по наличию в корзине."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart_recipe__user=user)
        return queryset

    def filter_favorites(self, queryset, name, value):
        """Фильтрация рецептов по избранному."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_by_tags(self, queryset, name, value):
        """Фильтрация рецептов по тегам."""
        tags = self.request.GET.getlist('tags')
        if tags:
            q_objects = Q()
            for tag in tags:
                q_objects |= Q(tags__slug=tag)
            queryset = queryset.filter(q_objects).distinct()
        return queryset
