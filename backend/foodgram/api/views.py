from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api.serializers import RecipeSerializer, IngredientSerializer, TagSerializer, CustomUserCreateSerializer
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingCart, Tag
)
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с обьектами класса User и подписки на авторов."""
    pass

    # queryset = User.objects.all()
    # serializer_class = CustomUserSerializer
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    # pagination_class = LimitOffsetPagination

    # @action(
    #     detail=False,
    #     methods=('get',),
    #     permission_classes=(IsAuthenticated, ),
    #     url_path='subscriptions',
    #     url_name='subscriptions',
    # )
    # def subscriptions(self, request):
    #     """Метод для создания страницы подписок"""

    #     queryset = User.objects.filter(follow__user=self.request.user)
    #     if queryset:
    #         pages = self.paginate_queryset(queryset)
    #         serializer = FollowSerializer(pages, many=True,
    #                                       context={'request': request})
    #         return self.get_paginated_response(serializer.data)
    #     return Response('Вы ни на кого не подписаны.',
    #                     status=status.HTTP_400_BAD_REQUEST)

    # @action(
    #     detail=True,
    #     methods=('post', 'delete'),
    #     permission_classes=(IsAuthenticated,),
    #     url_path='subscribe',
    #     url_name='subscribe',
    # )
    # def subscribe(self, request, id):
    #     """Метод для управления подписками """

    #     user = request.user
    #     author = get_object_or_404(User, id=id)
    #     change_subscription_status = Follow.objects.filter(
    #         user=user.id, author=author.id
    #     )
    #     if request.method == 'POST':
    #         if user == author:
    #             return Response('Вы пытаетесь подписаться на себя!!',
    #                             status=status.HTTP_400_BAD_REQUEST)
    #         if change_subscription_status.exists():
    #             return Response(f'Вы теперь подписаны на {author}',
    #                             status=status.HTTP_400_BAD_REQUEST)
    #         subscribe = Follow.objects.create(
    #             user=user,
    #             author=author
    #         )
    #         subscribe.save()
    #         return Response(f'Вы подписались на {author}',
    #                         status=status.HTTP_201_CREATED)
    #     if change_subscription_status.exists():
    #         change_subscription_status.delete()
    #         return Response(f'Вы отписались от {author}',
    #                         status=status.HTTP_204_NO_CONTENT)
    #     return Response(f'Вы не подписаны на {author}',
    #                     status=status.HTTP_400_BAD_REQUEST)


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
