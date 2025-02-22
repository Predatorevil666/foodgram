import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.constants import MAX_LENGTH
from api.utils import is_item_in_user_list
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Subscription


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
    # avatar = serializers.ImageField(use_url=True, required=False, allow_null=True)
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
        """Метод проверки подписки."""
        user = self.context.get('request').user
        return not user.is_anonymous and Subscription.is_subscribed(user, obj)


class CustomUserSerializer(BaseUserSerializer):
    """Сериализатор для чтения данных пользователя."""

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields


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
            'avatar',
            'is_subscribed',
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
        if value.lower() == "me":
            raise serializers.ValidationError("Имя 'me' запрещено.")
        return value

    def create(self, validated_data):
        """Создание нового пользователя и хэширование пароля."""
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
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
    """Сериализатор для работы с ингредиентами в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
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

# class IngredientInRecipeSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для отображения полной информации об ингредиентах в рецептах.
#     """

#     ingredient = IngredientSerializer()

#     class Meta:
#         model = IngredientInRecipe
#         fields = ('ingredient', 'amount')


# class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         queryset=Ingredient.objects.all(),
#         source='ingredient'
#     )
#     amount = serializers.IntegerField(
#         min_value=1,
#         source='amount'
#     )

#     class Meta:
#         model = IngredientInRecipe
#         fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientInRecipeSerializer(many=True)
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
        read_only_fields = ('author',)
        extra_kwargs = {
            'name': {'required': True, 'max_length': MAX_LENGTH},
            'text': {'required': True}
        }

    def validate_tags(self, value):
        """Проверка тегов."""
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы один тег")
        # elif len(value) > 3:
        #     raise serializers.ValidationError("Максимум 3 тега.")
        return value

    def validate_ingredients(self, value):
        """Проверка ингредиентов."""
        if not value:
            raise serializers.ValidationError("Добавьте ингредиенты")
        ingredients = [item['ingredient'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться")
        return value

    def get_ingredients_data(self, ingredients, recipe):
        """Получение данных ингредиентов для создания рецепта."""
        ingredients_data = []
        for ingredient_orderdict in ingredients:
            ingredient = ingredient_orderdict.get('ingredient')
            amount = int(ingredient_orderdict.get('amount'))
            recipe_ingredient = IngredientInRecipe(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
            ingredients_data.append(recipe_ingredient)
        return ingredients_data

    def to_representation(self, instance):
        """Преобразование экземпляра рецепта в сериализованный вид."""
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def create(self, validated_data):
        """Создание нового рецепта."""
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data.pop("author", None)
        validated_data['cooking_time'] = int(validated_data['cooking_time'])
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients_data
        ])
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
    # image = serializers.ImageField(use_url=True)
    image = Base64ImageField(use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'cooking_time',
            'ingredients', 'tags', 'image', 'author',
            'is_favorited', 'is_in_shopping_cart', 'pub_date'
        )

    def get_is_favorited(self, obj) -> bool:
        """Метод проверки на добавление в избранное."""
        user = self.context['request'].user
        return is_item_in_user_list(obj, Favorite, user)

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Метод проверки на присутствие в корзине."""
        user = self.context['request'].user
        return is_item_in_user_list(obj, ShoppingCart, user)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка подписок."""

    class Meta:
        model = Subscription
        fields = ('author', 'created_at')


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новой подписки."""

    class Meta:
        model = Subscription
        fields = ('author',)


class AddFavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное по модели Recipe."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time')
