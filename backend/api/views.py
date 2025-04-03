from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from django.urls import reverse
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageNumberLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             RecipeWriteSerializer, SubscriptionSerializer,
                             TagSerializer, UserSerializer)
from api.utils import add_to_user_list, remove_from_user_list
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с обьектами класса User."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberLimitPagination
    serializer_class = UserSerializer

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
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=AvatarSerializer
    )
    def update_avatar(self, request):
        """Управление аватаром пользователя."""
        user = request.user
        serializer = self.get_serializer(
            user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        user = request.user
        if not user.avatar:
            return Response(
                {'detail': 'Аватар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    pagination_class = PageNumberLimitPagination
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

        if user.is_authenticated:
            return recipes.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=user, recipe=OuterRef('pk'))),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user=user, recipe=OuterRef('pk')))
            )
        return recipes.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField())
        )

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора."""
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_short_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = request.build_absolute_uri(
            reverse('recipes:short-link-redirect', args=[recipe.slug])
        )
        return Response({'short-link': short_url})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Управление избранным."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return add_to_user_list(
                model=Favorite,
                serializer_class=RecipeShortSerializer,
                user=request.user,
                recipe=recipe
            )

        return remove_from_user_list(
            model=Favorite,
            user=request.user,
            recipe=recipe
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """Управление списком покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return add_to_user_list(
                model=ShoppingCart,
                serializer_class=RecipeShortSerializer,
                user=request.user,
                recipe=recipe
            )
        return remove_from_user_list(
            model=ShoppingCart,
            user=request.user,
            recipe=recipe
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
        ).annotate(total=Sum('amount')
                   ).order_by('ingredient__name')
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')


# class RecipeRedirectView(RedirectView):
#     """Вьюсет для редиректа."""

#     permanent = True

#     def get_redirect_url(self, *args, **kwargs):
#         recipe = get_object_or_404(Recipe, slug=kwargs['slug'])
#         # Перенаправляем на детальное представление рецепта
#         return reverse('api:recipe-detail', kwargs={'pk': recipe.id})


# class RecipeDetailView(RetrieveAPIView):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeReadSerializer
#     lookup_field = 'pk'


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
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        return User.objects.filter(
            subscribed__user=self.request.user
        ).annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes').order_by('username')

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        try:
            author = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        if user == author:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        _, created = Subscription.objects.get_or_create(
            user=user, author=author)

        if not created:
            return Response(
                {'error': 'Вы уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(author)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        try:
            author = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_count = Subscription.objects.filter(
            user=request.user,
            author=author
        ).delete()[0]

        if not deleted_count:
            return Response(
                {'error': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
