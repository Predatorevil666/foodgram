from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
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
    email = models.EmailField(
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
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/default_avatar.png'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    def delete_avatar(self):
        """Метод для удаления аватара."""
        if self.avatar:
            self.avatar.delete(save=False)
            self.avatar = None
            self.save()


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
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def is_subscribed(cls, user, author):
        """Проверка подписки."""
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

    def clean(self):
        """Проверка на попытку подписаться на самого себя."""
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя!')
        return super().clean()
