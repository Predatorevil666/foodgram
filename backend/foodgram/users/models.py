from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import EMAIL_LENGTH, USER_LENGTH
from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователей."""

    username = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Имя пользователя',
        blank=False,
        unique=True,
        db_index=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username,
        ],

    )
    email = models.CharField(
        max_length=EMAIL_LENGTH,
        verbose_name='Адрес электронной почты',
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_LENGTH,
        verbose_name='Фамилия'
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
        verbose_name="Автор рецепта",
    )

    @classmethod
    def is_subscribed(cls, user, author):
        return cls.objects.filter(user=user, author=author).exists()

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"],
                name="unique_subscription"
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
