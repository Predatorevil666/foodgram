from rest_framework.response import Response
from rest_framework import status
from recipes.models import Recipe


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
