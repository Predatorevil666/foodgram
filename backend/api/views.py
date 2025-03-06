from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AddFavoritesSerializer, AvatarSerializer,
                             CustomUserCreateSerializer, CustomUserSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, SubscriptionSerializer,
                             TagSerializer)
from api.utils import check_if_exists
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, mixins, permissions, status, viewsets
# from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с обьектами класса User."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    # authentication_classes = [TokenAuthentication]

    # def get_authenticators(self):
    #     if self.action == 'retrieve':
    #         return []
    #     return [TokenAuthentication()]

    def get_permissions(self):
        # if self.action in ['list', 'retrieve']:
        #     return [permissions.AllowAny()]
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        # return [permissions.IsAuthenticated()]
        return super().get_permissions()

    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'manage_avatar':
            return AvatarSerializer
        return CustomUserSerializer

    # @action(
    #     detail=False,
    #     methods=['get'],
    #     permission_classes=(IsAuthenticated,)
    # )
    # def me(self, request):
    #     serializer = self.get_serializer(
    #         request.user,
    #         context={'request': request}
    #     )
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
        serializer_class=AvatarSerializer
    )
    def manage_avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {"avatar": "Это поле обязательно."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                user, data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Аватар не найден'},
                status=status.HTTP_404_NOT_FOUND
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
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('delete',),
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def delete_recipe(self, request, pk=None):
        recipe = self.get_object()
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get_short_link'
    )
    def get_short_link(self, request, pk=None):
        """Генерация короткой ссылки на рецепт."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        return Response(
            {'short_link': serializer.data.get('short_link')},
            status=status.HTTP_200_OK
        )

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
            recipe_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'ID рецепта должно быть числом.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if check_if_exists(Favorite, user, recipe):
                return Response(
                    {'errors': f'Повторно "{recipe.name}" добавить нельзя, '
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
    def shopping_cart(self, request, pk=None):
        """Метод для управления списком покупок."""

        user = request.user
        try:
            recipe_id = int(pk)
            recipe = Recipe.objects.get(pk=recipe_id)
        except (ValueError, Recipe.DoesNotExist):
            return Response(
                {'error': 'Неверный ID рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if check_if_exists(ShoppingCart, user, recipe):
                return Response(
                    {'errors': f'Повторно "{recipe.name}" добавить нельзя, '
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
            recipe__shoppingcart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))
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


class SubscriptionViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для управления подписками."""

    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""
        return Subscription.objects.filter(
            user=self.request.user
        ).select_related('author').order_by('author__username')

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        """Обработка подписки/отписки."""
        author = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=request.user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.create(
                user=request.user,
                author=author
            )
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Subscription.objects.filter(
                user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
