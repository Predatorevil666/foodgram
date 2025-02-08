from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    AvatarUpdateSerializer,
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    SubscriptionSerializer,
    CreateSubscriptionSerializer
)
from api.permissions import IsAuthorOrReadOnly, IsAdminUserOrReadOnly
from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingCart, Tag
)
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с обьектами класса User."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора. """
        if self.action == 'post':
            return CustomUserCreateSerializer
        return CustomUserSerializer


class AvatarUpdateViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки запросов на смену аватара."""

    queryset = User.objects.all()
    serializer_class = AvatarUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['tags', 'author', 'cooking_time']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Генерация короткой ссылки
        short_link = request.build_absolute_uri(f'/recipes/{instance.slug}/')

        return Response({
            'recipe': serializer.data,
            'short_link': short_link
        })


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для покупок"""

    queryset = ShoppingCart.objects.all()
    serializer_class = IngredientSerializer


# class FavoriteViewSet(viewsets.ModelViewSet):
#     """Вьюсет для избранного"""

#     queryset = Favorite.objects.all()
#     serializer_class = IngredientSerializer
#     permission_classes = (IsAuthenticated,)


class SubscriptionViewSet(viewsets.ViewSet):
    """Вьюсет для управления подписками."""

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        Получить список авторов, на которых подписан пользователь.
        """
        subscriptions = Subscription.objects.filter(
            user=request.user).select_related('author')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Подписаться на автора."""
        serializer = CreateSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            author = serializer.validated_data['author']
            if not Subscription.objects.filter(
                    user=request.user,
                    author=author
            ).exists():
                subscription = Subscription.objects.create(
                    user=request.user, author=author)
                return Response(
                    SubscriptionSerializer(subscription).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'detail': 'Вы уже подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk=None):
        """Отписаться от автора."""
        try:
            subscription = Subscription.objects.get(
                user=request.user, author_id=pk)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )
