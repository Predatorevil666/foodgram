import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Метод проверки подписки."""
        user = self.context.get('request').user
        return not user.is_anonymous and Subscription.is_subscribed(user, obj)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
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

    def create(self, validated_data):
        """Создание нового пользователя и хэширование пароля."""
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    """Обработка изображения в формате Base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientInRecipe
        fields = ['ingredient', 'quantity']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            IngredientInRecipe.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        instance.ingredient_list.all().delete()

        for ingredient_data in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=instance, **ingredient_data)

        return instance
