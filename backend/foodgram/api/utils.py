def is_item_in_user_list(obj, model, user):
    """Общий метод для проверки наличия элемента в списке пользователя."""
    if user.is_anonymous:
        return False
    return model.objects.filter(user=user, recipe=obj).exists()


def check_if_exists(model, user, recipe):
    """Метод для проверки на существование обьекта."""
    return model.objects.filter(user=user, recipe=recipe).exists()
