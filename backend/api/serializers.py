import base64

from api.constants import MAX_LENGTH
from api.utils import is_item_in_user_list
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription
import logging
logger = logging.getLogger(__name__)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Обработка изображения в формате Base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')

        return super().to_internal_value(data)


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: tuple[str, ...] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    # def get_is_subscribed(self, obj):
    #     """Проверка подписки только для аутентифицированных пользователей"""
    #     user = self.context.get('request').user
    #     if user.is_authenticated:
    #         return Subscription.is_subscribed(user, obj)
    #     return False
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        # Явная проверка, что пользователь аутентифицирован
        if not user.is_authenticated:
            return False
        return Subscription.is_subscribed(user, obj)


class CustomUserSerializer(BaseUserSerializer):
    """Сериализатор для чтения данных пользователя."""

    avatar = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None


class CustomUserCreateSerializer(BaseUserSerializer):
    """Сериализатор для создания нового пользователя."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8
    )

    class Meta(BaseUserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'first_name': {
                'required': True,
                'allow_blank': False,
                'min_length': 2,
            },
            'last_name': {
                'required': True,
                'allow_blank': False,
                'min_length': 2,
            },
            'email': {
                'required': True,
                'allow_blank': False,
            },
            'username': {
                'required': True,
                'allow_blank': False,
                'min_length': 3,
            },
            'password': {
                'required': True,
                'write_only': True,
                'min_length': 8,
            }
        }

    def validate_email(self, value):
        """Проверка, что email уникален."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Данный email уже используется.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient"
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        """Преобразуем входные данные для модели"""
        data["ingredient"] = data.pop("id")
        return super().to_internal_value(data)

    def validate_ingredient(self, value):
        if not value:
            raise serializers.ValidationError("Укажите ингредиент")
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'name', 'text', 'cooking_time',
            'ingredients', 'tags', 'image', 'author'
        )
        read_only_fields = ('author', 'slug')
        extra_kwargs = {
            'name': {'required': True, 'max_length': MAX_LENGTH},
            'text': {'required': True}
        }

    def validate_tags(self, value):
        """Проверка тегов."""
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы один тег")
        elif len(value) > 4:
            raise serializers.ValidationError("Максимум 4 тега.")
        return value

    # def validate_ingredients(self, value):
    #     """Валидация ингредиентов."""
    #     if not isinstance(value, list):
    #         raise serializers.ValidationError(
    #             "Ингредиенты должны быть списком объектов."
    #         )

    #     seen_ids = set()
    #     for item in value:
    #         if "id" not in item or "amount" not in item:
    #             raise serializers.ValidationError(
    #                 "Каждый ингредиент должен содержать поля 'id' и 'amount'."
    #             )
    #         if item["id"] in seen_ids:
    #             raise serializers.ValidationError(
    #                 f"Ингредиент с ID {item['id']} указан повторно."
    #             )
    #         seen_ids.add(item["id"])
    #     return value
    # def validate_ingredients(self, value):
    #     """Проверка уникальности ингредиентов."""
    #     if not value:
    #         raise serializers.ValidationError(
    #             "Добавьте хотя бы один ингредиент")

    #     ingredients = [item['ingredient'].id for item in value]
    #     if len(ingredients) != len(set(ingredients)):
    #         raise serializers.ValidationError(
    #             "Ингредиенты не должны повторяться")

    #     return value
    def validate_ingredients(self, value):
        """Проверка уникальности ингредиентов."""
        logger.debug(f"Received ingredients data: {value}")
        ingredients = [item["ingredient"]["id"] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться.")
        return value

    # def create(self, validated_data):
    #     """Создание рецепта с ингредиентами."""
    #     ingredients_data = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     recipe.tags.set(tags)

    #     ingredients = [
    #         IngredientInRecipe(
    #             recipe=recipe,
    #             ingredient=item['ingredient'],
    #             amount=item['amount']
    #         ) for item in ingredients_data
    #     ]
    #     IngredientInRecipe.objects.bulk_create(ingredients)

    #     return recipe
    def create(self, validated_data):
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        # Создаем рецепт
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        # Создаем связи с ингредиентами
        ingredients = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item["ingredient"],  # Объект Ingredient
                amount=item["amount"]
            )
            for item in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(ingredients)

        return recipe

    def update(self, instance, validated_data):
        """Обновление существующего рецепта."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.ingredient_list.all().delete()
            IngredientInRecipe.objects.bulk_create([
                IngredientInRecipe(
                    recipe=instance,
                    ingredient=item['ingredient'],
                    amount=item['amount']
                ) for item in ingredients_data
            ])
        return instance


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_list'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField(use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'cooking_time',
            'ingredients', 'tags', 'image', 'author',
            'is_favorited', 'is_in_shopping_cart', 'pub_date', 'short_link',
        )

    def get_is_favorited(self, obj) -> bool:
        """Метод проверки на добавление в избранное."""
        user = self.context['request'].user
        return is_item_in_user_list(obj, Favorite, user)

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Метод проверки на присутствие в корзине."""
        user = self.context['request'].user
        return is_item_in_user_list(obj, ShoppingCart, user)

    def get_short_link(self, obj):
        """Генерация короткой ссылки."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/recipes/{obj.slug}/')
        return None


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для рецептов (используется в подписках)."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        """
        Список рецептов с поддержкой лимита через параметр `recipes_limit`.
        """
        request = self.context.get('request')
        recipes = obj.author.recipes.all()
        if 'recipes_limit' in request.query_params:
            try:
                limit = int(request.query_params['recipes_limit'])
                recipes = recipes[:limit]
            except ValueError:
                pass

        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class AddFavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное по модели Recipe."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
        extra_kwargs = {
            'avatar': {
                'required': True,
                'allow_null': False
            }
        }

    def to_representation(self, instance):
        return {
            'avatar': self.context['request'].build_absolute_uri(
                instance.avatar.url
            )
            if instance.avatar else None
        }
