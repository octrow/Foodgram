from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models.functions import Length

from core import texts
from core.limits import Limits

models.CharField.register_lookup(Length)

CustomUser = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=Limits.MAX_LEN_150.value,
        help_text=texts.INGREDIENT_NAME_HELP_TEXT,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=Limits.MAX_LEN_32.value,
        help_text=texts.INGREDIENT_MEASUREMENT_UNIT_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега",
        unique=True,
        max_length=Limits.MAX_LEN_200.value,
        help_text=texts.TAG_NAME_HELP_TEXT,
    )
    color = models.CharField(
        verbose_name="HEX-код",
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Введенное значение не является цветом в формате HEX!",
            )
        ],
        help_text=texts.TAG_COLOR_HELP_TEXT,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
        max_length=Limits.MAX_LEN_200.value,
        help_text=texts.TAG_SLUG_HELP_TEXT,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=Limits.MAX_LEN_200.value,
        help_text=texts.RECIPE_NAME_HELP_TEXT,
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
        help_text=texts.RECIPE_IMAGE_HELP_TEXT,
    )
    text = models.TextField(
        verbose_name="Описание", help_text=texts.RECIPE_TEXT_HELP_TEXT
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text=texts.RECIPE_AUTHOR_HELP_TEXT,
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(1, message="Минимум 1 минута!"),
            MaxValueValidator(10080, message="Максимум 7 дней!"),
        ],
        help_text=texts.RECIPE_COOKING_TIME_HELP_TEXT,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes",
        blank=True,
        help_text=texts.RECIPE_TAGS_HELP_TEXT,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиенты",
        related_name="recipes",
        through="AmountIngredient",
        help_text=texts.RECIPE_INGREDIENTS_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredient",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text=texts.AMOUNT_INGREDIENT_RECIPE_HELP_TEXT,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        help_text=texts.AMOUNT_INGREDIENT_INGREDIENT_HELP_TEXT,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        help_text=texts.AMOUNT_INGREDIENT_AMOUNT_HELP_TEXT,
        validators=(MinValueValidator(1, message="Должно быть больше нуля"),),
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты рецепта"
        ordering = ("recipe",)

    def __str__(self):
        return (
            f"{self.ingredient.name} ({self.ingredient.measurement_unit}) - "
            f"{self.amount} "
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorite",
        help_text=texts.FAVORITE_USER_HELP_TEXT,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="favorite",
        help_text=texts.FAVORITE_RECIPE_HELP_TEXT,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        editable=False,
        help_text=texts.FAVORITE_DATE_ADDED_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is favorite alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name="Пользователь",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        help_text=texts.SHOPPING_CART_USER_HELP_TEXT,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        help_text=texts.SHOPPING_CART_RECIPE_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="\n%(app_label)s_%(class)s recipe is cart alredy\n",
            ),
        )

    def __str__(self):
        return f"{self.recipe} в корзине у {self.user}"
