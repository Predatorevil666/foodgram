from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, CustomUserCreateSerializer,
                             CustomUserSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeShortLinkSerializer, RecipeWriteSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer)
from api.utils import create_or_update_recipe, get_recipe, manage_user_list
from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с обьектами класса User."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'manage_avatar':
            return AvatarSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=["post"],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(
            request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=AvatarSerializer
    )
    def manage_avatar(self, request):
        """Управление аватаром пользователя."""
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

    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Получение списка рецептов с учетом подписок и избранного."""
        user = self.request.user
        recipes = Recipe.objects.prefetch_related(
            'ingredient_list__ingredient',
            'tags',
            'author'
        ).all()

        # if user.is_authenticated:
        #     return recipes.annotate(
        #         is_favorited=Exists(Favorite.objects.filter(
        #             user=user, recipe=OuterRef('pk'))),
        #         is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
        #             user=user, recipe=OuterRef('pk')))
        #     )
        # return recipes.annotate(
        #     is_favorited=Value(False, output_field=BooleanField()),
        #     is_in_shopping_cart=Value(False, output_field=BooleanField())
        # )

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора."""
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        """Создание рецепта."""
        return create_or_update_recipe(
            RecipeWriteSerializer,
            request
        )

    def update(self, request, *args, **kwargs):
        """Обновление рецепта."""
        instance = self.get_object()
        return create_or_update_recipe(
            RecipeWriteSerializer,
            request,
            instance
        )

    def retrieve(self, request, *args, **kwargs):
        """Получение подробной информации о рецепте."""
        instance = self.get_object()
        logger.debug(f"Получение подробной информации о рецепте: {instance}")
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
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        serializer = RecipeShortLinkSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        recipe, error_response = get_recipe(pk)
        if error_response:
            return error_response

        return manage_user_list(
            model=Favorite,
            serializer_class=FavoriteSerializer,
            user=user,
            recipe=recipe,
            request_method=request.method
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
        recipe, error_response = get_recipe(pk)
        if error_response:
            return error_response

        return manage_user_list(
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
            user=user,
            recipe=recipe,
            request_method=request.method
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
        user = request.user
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.create(
                user=user,
                author=author
            )
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            ).first()
            if not subscription:
                return Response(
                    {'errors': 'Вы не подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
