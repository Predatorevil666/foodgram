from recipes.models import IngredientInRecipe, Recipe
from rest_framework import serializers, status
from rest_framework.response import Response


def is_item_in_user_list(obj, model, user):
    """Общий метод для проверки наличия элемента в списке пользователя."""
    if user.is_anonymous:
        return False
    return model.objects.filter(user=user, recipe=obj).exists()


def check_if_exists(model, user, recipe):
    """Метод для проверки на существование обьекта."""
    return model.objects.filter(user=user, recipe=recipe).exists()


def manage_user_list(model, serializer_class, user, recipe, request_method):
    """Общий метод для управления избранным и списком покупок."""
    if request_method == 'POST':
        if check_if_exists(model, user, recipe):
            return Response(
                {'errors': f'Повторно "{recipe.name}" добавить нельзя, '
                 f'он уже есть в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = serializer_class(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request_method == 'DELETE':
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепт "{recipe.name}" отсутствует в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )


def get_recipe(pk):
    """Получение рецепта по ID с обработкой ошибок."""
    try:
        recipe_id = int(pk)
        recipe = Recipe.objects.get(pk=recipe_id)
        return recipe, None
    except ValueError:
        return None, Response(
            {'error': 'ID рецепта должно быть числом.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Recipe.DoesNotExist:
        return None, Response(
            {'errors': 'Рецепт не найден.'},
            status=status.HTTP_404_NOT_FOUND
        )


def create_or_update_recipe(serializer, request, instance=None):
    """
    Универсальная функция для создания или обновления рецепта.
    """
    from api.serializers import RecipeReadSerializer
    if instance:
        serializer_instance = serializer(
            instance, data=request.data, partial=False)
    else:
        serializer_instance = serializer(data=request.data)

    serializer_instance.is_valid(raise_exception=True)
    serializer_instance.save(author=request.user)
    read_serializer = RecipeReadSerializer(
        serializer_instance.instance,
        context={'request': request}
    )
    return Response(
        read_serializer.data,
        status=status.HTTP_201_CREATED if not instance else status.HTTP_200_OK
    )


def validate_not_empty(value, field_name):
    """
    Универсальная функция для проверки, что поле не пустое.
    """
    if not value:
        raise serializers.ValidationError(
            {field_name: f"Добавьте хотя бы один {field_name}."}
        )
    return value


def processing_recipe_ingredients_and_tags(
    recipe,
    ingredients_data,
    tags
):
    """
    Универсальная функция для обрабатки ингредиентов и тегов рецепта.
    """
    recipe.tags.set(tags)
    if recipe.pk:
        recipe.ingredient_list.all().delete()
    ingredients = [
        IngredientInRecipe(
            recipe=recipe,
            ingredient=item['ingredient'],
            amount=item['amount']
        ) for item in ingredients_data
    ]
    IngredientInRecipe.objects.bulk_create(ingredients)

    return recipe
