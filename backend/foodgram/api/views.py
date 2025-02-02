from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers import RecipeSerializer, IngredientSerializer, TagSerializer
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingCart, Tag
)
from users.models import Subscription


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для покупок"""
    queryset = ShoppingCart.objects.all()
    serializer_class = IngredientSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для избранного"""
    queryset = Favorite.objects.all()
    serializer_class = IngredientSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Вьюсет для подписки"""
    queryset = Subscription.objects.all()
    serializer_class = IngredientSerializer
