import logging
from django.db.models import Q
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet, NumberFilter)

from recipes.models import Ingredient, Recipe, Tag
logger = logging.getLogger(__name__)


class IngredientFilter(FilterSet):
    """Фильтр для модели ингредиентов."""

    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


# class RecipeFilter(FilterSet):
#     """Фильтр для модели рецептов."""

#     author = NumberFilter(field_name='author__id')
#     tags = CharFilter(field_name='tags__slug', method='filter_by_tags')
#     is_favorited = BooleanFilter(method='filter_favorites')
#     is_in_shopping_cart = BooleanFilter(
#         method="filter_shopping_cart",
#         field_name='shopping_recipe'
#     )

#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

#     def filter_shopping_cart(self, queryset, name, value):
#         """Фильтрация рецептов по наличию в корзине."""
#         user = self.request.user
#         if value and user.is_authenticated:
#             return queryset.filter(shoppingcart_recipe__user=user)
#         return queryset

#     def filter_favorites(self, queryset, name, value):
#         """Фильтрация рецептов по избранному."""
#         user = self.request.user
#         if value and user.is_authenticated:
#             return queryset.filter(favorite_recipe__user=user)
#         return queryset

#     def filter_by_tags(self, queryset, name, value):
#         """Фильтрация рецептов по тегам."""
#         tags = self.request.GET.getlist('tags')
#         if tags:
#             q_objects = Q()
#             for tag in tags:
#                 q_objects |= Q(tags__slug=tag)
#             queryset = queryset.filter(q_objects).distinct()
#         logger.debug(f"Отфильтрованные рецепты: {queryset}")
#         return queryset
# from django_filters.rest_framework import (
#     BooleanFilter,
#     CharFilter,
#     FilterSet,
#     NumberFilter,
# )
# from recipes.models import Ingredient, Recipe


# class IngredientFilter(FilterSet):
#     name = CharFilter(field_name='name', lookup_expr='istartswith')

#     class Meta:
#         model = Ingredient
#         fields = ('name',)


# class RecipeFilter(FilterSet):
#     author = NumberFilter(field_name='author__id')
#     tags = CharFilter(field_name='tags__slug', lookup_expr='iexact')
#     is_favorited = BooleanFilter(field_name='favorite_recipe__user')
#     is_in_shopping_cart = BooleanFilter(field_name='shoppingcart_recipe__user')

#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

# class RecipeFilter(FilterSet):
#     tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
#                                              to_field_name='slug',
#                                              queryset=Tag.objects.all())
#     is_favorited = filters.NumberFilter(
#         method='is_favorited_filter')
#     is_in_shopping_cart = filters.NumberFilter(
#         method='is_in_shopping_cart_filter')

#     class Meta:
#         model = Recipe
#         fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

#     def is_favorited_filter(self, queryset, name, value):
#         queryset.add_user_annotations(self.request.user.id)
#         if value and self.request.user.is_authenticated:
#             return queryset.filter(favorite_recipe__user=self.request.user)
#         return queryset

#     def is_in_shopping_cart_filter(self, queryset, name, value):
#         queryset.add_user_annotations(self.request.user.id)
#         if value and self.request.user.is_authenticated:
#             return queryset.filter(shoppingcart_recipe__user=self.request.user)
#         return queryset
# class OneZeroFilter(BooleanFilter):
#     """Фильтр для преобразования значений 0 и 1 в булевы значения."""

#     def filter(self, qs, value):
#         if value == '1':
#             value = True
#         elif value == '0':
#             value = False
#         return super().filter(qs, value)


# class RecipeFilter(FilterSet):
#     """Фильтр для модели рецептов."""

#     author = NumberFilter(field_name='author__id')
#     tags = CharFilter(field_name='tags__slug', method='filter_by_tags')
#     # is_favorited = BooleanFilter(method='filter_favorites')
#     # is_in_shopping_cart = OneZeroFilter(field_name='is_in_shopping_cart')
#     is_favorited = filters.NumberFilter(
#         method='is_favorited_filter')
#     is_in_shopping_cart = filters.NumberFilter(
#         method='is_in_shopping_cart_filter')

#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

#     def is_favorited_filter(self, queryset, name, value):
#         """Фильтрация рецептов по избранному."""
#         user = self.request.user
#         if value:
#             return queryset.filter(favorite_recipe__user=user)
#         return queryset

#     def is_in_shopping_cart_filter(self, queryset, name, value):
#         """Фильтрация рецептов по наличию в корзине."""
#         user = self.request.user
#         if value and user.is_authenticated:
#             return queryset.filter(shoppingcart_recipe__user=user)
#         return queryset

#     def filter_by_tags(self, queryset, name, value):
#         """Фильтрация рецептов по тегам."""
#         tags = self.request.GET.getlist('tags')
#         return queryset.filter(tags__slug__in=tags).distinct()

class RecipeFilter(FilterSet):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n\n\n\n\n\n\n\n')
    author = NumberFilter(field_name='author__id')
    # tags = CharFilter(field_name='tags__slug', lookup_expr='iexact')
    # tags = filters.ModelMultipleChoiceFilter(
    #     field_name='tags__slug',
    #     to_field_name='slug',
    #     queryset=Tag.objects.all(),
    # )
    tags = CharFilter(field_name='tags__slug', method='filter_tags')
    is_favorited = NumberFilter(
        field_name='is_favorited')
    is_in_shopping_cart = NumberFilter(
        field_name='is_in_shopping_cart')
    # is_favorited = filters.BooleanFilter()
    # is_in_shopping_cart = filters.BooleanFilter()

    # def filter_tags(self, queryset, name, value):
    #     """Фильтрация по тегам с обработкой '#'."""
    #     print('22222222222222222222222222222222222222222222222222222222\n\n\n\n\n\n\n\n\n')
    #     # print(f'Queryset: {queryset.__dict__}')
    #     tags = self.request.GET.getlist('tags')
    #     if tags:
    #         q_objects = Q()
    #         for tag in tags:
    #             q_objects |= Q(tags__slug=tag)
    #         queryset = queryset.filter(q_objects).distinct()
    #     return queryset
    
    def filter_by_tags(self, queryset, name, value):
        """Фильтрация рецептов по тегам."""
        tags = self.request.GET.getlist('tags')
        logger.debug(f"Теги из запроса: {tags}")
        return queryset.filter(tags__slug__in=tags).distinct()

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
