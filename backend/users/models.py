from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models

from core import texts
from core.limits import Limits


class CustomUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "password", "username")

    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
        max_length=Limits.MAX_LEN_254.value,
        validators=[EmailValidator],
        help_text=texts.CUSTOM_USER_EMAIL_HELP_TEXT,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=Limits.MAX_LEN_150.value,
        help_text=texts.CUSTOM_USER_FIRST_NAME_HELP_TEXT,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=Limits.MAX_LEN_150.value,
        help_text=texts.CUSTOM_USER_LAST_NAME_HELP_TEXT,
    )
    username = models.CharField(
        verbose_name="Никнейм",
        unique=True,
        max_length=Limits.MAX_LEN_150.value,
        help_text=texts.CUSTOM_USER_USERNAME_HELP_TEXT,
    )
    is_active = models.BooleanField(
        verbose_name="Активирован",
        default=True,
        help_text=texts.CUSTOM_USER_IS_ACTIVE_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
        constraints = (
            models.UniqueConstraint(
                fields=("username", "email"),
                name="\n%(app_label)s_%(class)s username and email must be unique\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    date_added = models.DateTimeField(
        verbose_name="Дата подписки",
        auto_now_add=True,
        help_text=texts.SUBSCRIPTION_DATE_ADDED_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"),
                name="\n%(app_label)s_%(class)s user cannot subscribe to same author twice\n",
            ),
        )

    def __str__(self):
        return f"Пользователь {self.user} подписался на {self.author}"

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValueError("Нельзя подписаться на самого себя")
        super().save(*args, **kwargs)
