from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import IngredientInRecipe


def add_to_user_list(model, serializer_class, user, recipe):
    """
    Метод для добавления рецепта в пользовательский список
    (избранное/корзину).
    """
    _, created = model.objects.get_or_create(user=user, recipe=recipe)
    if not created:
        return Response(
            {'errors': f'Повторно "{recipe.name}" добавить нельзя, '
             f'он уже есть в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = serializer_class(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def remove_from_user_list(model, user, recipe):
    """
    Метод для удаления рецепта из пользовательского списка
    (избранного/корзины).
    """
    deleted_count, _ = model.objects.filter(user=user, recipe=recipe).delete()

    if deleted_count == 0:
        return Response(
            {'errors': f'Рецепт "{recipe.name}" отсутствует в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(status=status.HTTP_204_NO_CONTENT)


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
        recipe.ingredients.clear()
    ingredients = [
        IngredientInRecipe(
            recipe=recipe,
            ingredient=item['ingredient'],
            amount=item['amount']
        ) for item in ingredients_data
    ]
    IngredientInRecipe.objects.bulk_create(ingredients)

    return recipe
