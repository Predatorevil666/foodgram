from api.fields import Base64ImageField
from api.utils import (processing_recipe_ingredients_and_tags,
                       validate_not_empty)
from django.contrib.auth import get_user_model
from django.db import transaction
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


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

    def get_is_subscribed(self, obj):
        """Проверка подписки только для аутентифицированных пользователей."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.is_subscribed(request.user, obj)
        )


class UserSerializer(BaseUserSerializer):
    """Сериализатор для чтения данных пользователя."""

    avatar = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


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
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name', 'text', 'cooking_time',
            'ingredients', 'tags', 'image', 'author'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        """Общая валидация данных рецепта."""
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно."})
        if 'tags' not in data:
            raise serializers.ValidationError(
                {"tags": "Это поле обязательно."})
        return data

    def validate_tags(self, value):
        """Проверка тегов."""
        validate_not_empty(value, "tags")

        unique_tags = set(value)
        if len(unique_tags) != len(value):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."})

        return value

    def validate_ingredients(self, value):
        """Проверка ингредиентов."""
        validate_not_empty(value, "ingredients")

        ingredient_ids = [item['ingredient'].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."})

        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        processing_recipe_ingredients_and_tags(
            recipe,
            ingredients_data,
            tags
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление существующего рецепта."""
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        processing_recipe_ingredients_and_tags(
            instance,
            ingredients_data,
            tags
        )
        return instance

    def to_representation(self, instance):
        """Преобразуем объект через RecipeReadSerializer."""
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_list'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(use_url=True)
    is_favorited = serializers.BooleanField(
        default=False,
        read_only=True,
        help_text="Находится ли рецепт в избранном у текущего пользователя"
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False,
        read_only=True,
        help_text="Находится ли рецепт в списке покупок текущего пользователя"
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'cooking_time',
            'ingredients', 'tags', 'image', 'author',
            'is_favorited', 'is_in_shopping_cart',
        )


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


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписок с рецептами авторов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return obj.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
