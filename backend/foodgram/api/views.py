from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    AddFavoritesSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    IngredientSerializer,
    TagSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    SubscriptionSerializer,
    CreateSubscriptionSerializer
)
from api.permissions import IsAuthorOrReadOnly
from api.pagination import CustomPagination
from api.filters import IngredientFilter, RecipeFilter
from api.utils import check_if_exists
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe,
    ShoppingCart, Tag
)
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с обьектами класса User."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора. """
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def manage_avatar(self, request):
        """Управление аватаром пользователя (изменение или удаление)."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Аватар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.data:
            return Response(
                {'detail': 'Отсутствуют данные для обновления'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ['tags', 'author', 'cooking_time']

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора. """
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        """Сохранение рецепта с привязкой к автору."""
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Получение подробной информации о рецепте."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        short_link = request.build_absolute_uri(f'/recipes/{instance.slug}/')
        return Response({
            'recipe': serializer.data,
            'short_link': short_link
        })

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Метод для управления избранным."""
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if self.check_if_exists(Favorite, user, recipe):
                return Response(
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                     f'он уже есть в избранном у пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = Favorite.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'В избранном рецепта {recipe.name} нет'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Метод для управления списком покупок."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if self.check_if_exists(ShoppingCart, user, recipe):
                return Response(
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                     f'он уже есть в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Нельзя удалить рецепт - \"{recipe.name}\", '
                 f'которого нет в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Метод для объединения ингредиентов в список для загрузки."""

        shopping_list = 'Список покупок:\n\n'
        for item in ingredients:
            shopping_list += (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total']}\n"
            )
        return shopping_list

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Метод для загрузки ингредиентов и их количества
           для выбранных рецептов.
        """

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('quantity'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['^name']
    filterset_fields = ('name',)
    filterset_class = IngredientFilter


class SubscriptionViewSet(viewsets.ViewSet):
    """Вьюсет для управления подписками."""

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        Получить список авторов, на которых подписан пользователь.
        """

        user = User.objects.get(username=request.user)
        authors_list = user.follower.all()

        if authors_list:
            subscriptions = Subscription.objects.filter(
                user=request.user).select_related('author')
            serializer = SubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data)
        return Response(
            {'detail': 'Вы ни на кого не подписаны.'},
            status=status.HTTP_400_BAD_REQUEST
        )

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
