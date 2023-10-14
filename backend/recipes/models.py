from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length

from recipes.constants import MAX_HEX, MAX_LEN_TITLE, MAX_VALUE, MIN_VALUE
from users.models import User

models.CharField.register_lookup(Length)


class Ingredient(models.Model):
    NAME_HELP_TEXT = "Введите название ингредиента"
    MEASUREMENT_UNIT_HELP_TEXT = "Введите единицу измерения ингредиента"
    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LEN_TITLE,
        help_text=NAME_HELP_TEXT,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LEN_TITLE,
        help_text=MEASUREMENT_UNIT_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_unit"
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    NAME_HELP_TEXT = "Введите название тега"
    COLOR_HELP_TEXT = "Введите HEX-код цвета тега"
    SLUG_HELP_TEXT = "Введите уникальный идентификатор тега"
    name = models.CharField(
        verbose_name="Название тега",
        unique=True,
        max_length=MAX_LEN_TITLE,
        help_text=NAME_HELP_TEXT,
    )
    color = ColorField(
        verbose_name="HEX-код",
        max_length=MAX_HEX,
        unique=True,
        help_text=COLOR_HELP_TEXT,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
        max_length=MAX_LEN_TITLE,
        help_text=SLUG_HELP_TEXT,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    NAME_HELP_TEXT = "Введите название рецепта"
    AUTHOR_HELP_TEXT = "Выберите автора рецепта"
    IMAGE_HELP_TEXT = "Загрузите изображение рецепта"
    TEXT_HELP_TEXT = "Введите описание рецепта"
    COOKING_TIME_HELP_TEXT = "Введите время приготовления рецепта в минутах"
    TAGS_HELP_TEXT = "Выберите теги для рецепта"
    INGREDIENTS_HELP_TEXT = (
        "Выберите ингредиенты для рецепта и укажите их количество"
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=MAX_LEN_TITLE,
        help_text=NAME_HELP_TEXT,
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
        help_text=IMAGE_HELP_TEXT,
    )
    text = models.TextField(
        verbose_name="Описание", help_text=TEXT_HELP_TEXT
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text=AUTHOR_HELP_TEXT,
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(MIN_VALUE,
                              message=f"Минимум {MIN_VALUE} минута!"),
            MaxValueValidator(MAX_VALUE,
                              message=f"Максимум {MAX_VALUE} минут!"),
        ],
        help_text=COOKING_TIME_HELP_TEXT,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes",
        blank=True,
        help_text=TAGS_HELP_TEXT,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиенты",
        related_name="recipes",
        through="AmountIngredient",
        help_text=INGREDIENTS_HELP_TEXT,
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
    INGREDIENT_RECIPE_HELP_TEXT = (
        "Выберите рецепт, к которому относится ингредиент"
    )
    INGREDIENT_INGREDIENT_HELP_TEXT = (
        "Выберите ингредиент, который используется в рецепте"
    )
    INGREDIENT_AMOUNT_HELP_TEXT = (
        "Введите количество ингредиента в единицах измерения"
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredient",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text=INGREDIENT_RECIPE_HELP_TEXT,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        help_text=INGREDIENT_INGREDIENT_HELP_TEXT,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        help_text=INGREDIENT_AMOUNT_HELP_TEXT,
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message=f"Должно быть {MIN_VALUE} и больше"),
            MaxValueValidator(
                MAX_VALUE,
                message="Число должно быть меньше чем {settings.MAX_VALUE}")),
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


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name=("\n%(app_label)s_%(class)s recipe is"
                      " already related to user\n"),
            ),
        )


class Favorite(UserRecipeRelation):
    date_added = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        editable=False,
    )

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.user} добавил '{self.recipe}' в Избранное"


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"

    def __str__(self):
        return f"{self.recipe} в корзине у {self.user}"
