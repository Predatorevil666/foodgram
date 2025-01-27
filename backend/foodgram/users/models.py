from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import EMAIL_LENGTH, USERNAME_LENGTH
from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователей."""

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name='Уникальный юзернейм',
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username,
        ],

    )
    email = models.CharField(
        max_length=EMAIL_LENGTH,
        verbose_name='Адрес электронной почты',
        unique=True
    )
    first_name = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=100,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username[:50]
    

class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribed",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="user_cannot_follow_himself",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
