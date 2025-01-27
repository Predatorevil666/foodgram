from django.core.exceptions import ValidationError


def validate_username(value):
    """Проверяем, является ли имя пользователя зарезервированным."""

    reserved_username = 'me'
    if value == reserved_username:
        raise ValidationError(
            f'Имя "{value}" зарезервировано и не может быть использовано')
