from django.core.exceptions import ValidationError
from users.constants import RESERVED_USERNAME


def validate_username(value):
    """Проверяем, является ли имя пользователя зарезервированным."""

    if value == RESERVED_USERNAME:
        raise ValidationError(
            f'Имя "{value}" зарезервировано и не может быть использовано')
