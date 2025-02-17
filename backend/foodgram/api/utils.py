def is_item_in_user_list(self, obj, model):
    """Общий метод для проверки наличия элемента в списке пользователя."""
    request = self.context.get('request')
    if request is None or request.user.is_anonymous:
        return False
    return model.objects.filter(user=request.user, recipe=obj).exists()


def check_if_exists(self, model, user, recipe):
    """Метод для проверки на существование обьекта."""
    return model.objects.filter(user=user, recipe=recipe).exists()
