from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from recipes.constants import MAX_LEN_EMAIL, MAX_LEN_NAME


class User(AbstractUser):
    EMAIL_HELP_TEXT = "Введите вашу электронную почту"
    FIRST_NAME_HELP_TEXT = "Введите ваше имя"
    LAST_NAME_HELP_TEXT = "Введите вашу фамилию"
    USERNAME_HELP_TEXT = "Введите уникальное имя пользователя"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "password", "username")

    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
        max_length=MAX_LEN_EMAIL,
        validators=[EmailValidator],
        help_text=EMAIL_HELP_TEXT,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LEN_NAME,
        help_text=FIRST_NAME_HELP_TEXT,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LEN_NAME,
        help_text=LAST_NAME_HELP_TEXT,
    )
    username = models.CharField(
        verbose_name="Никнейм",
        unique=True,
        max_length=MAX_LEN_NAME,
        help_text=USERNAME_HELP_TEXT,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9]+([_.-]?[a-zA-Z0-9])*$",
                message=("Юзернейм может содержать только цифры, латинские"
                         " буквы, знаки (не в начале): тире, точка и "
                         "нижнее тире.")
            )]
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name="followed_users",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        related_name="author",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"),
                name=(
                    "\n%(app_label)s_%(class)s user cannot subscribe "
                    "to same author twice\n"),
            ),
        )

    def __str__(self):
        return f"Пользователь {self.user} подписался на {self.author}"

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValidationError("Нельзя подписаться на самого себя")
        super().save(*args, **kwargs)
