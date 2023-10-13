from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.constants import MAX_VALUE, MIN_VALUE

from .models import (AmountIngredient, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)

admin.site.site_header = "Администрирование Foodgram"
admin.site.unregister(Group)


class IngredientInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1
    min_num = MIN_VALUE
    max_num = MAX_VALUE
    validate_min = True
    validate_max = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_image",
        "cooking_time",
        "count_favorites",
        "get_ingredients",
    )
    fields = (
        (
            "name",
            "cooking_time",
        ),
        (
            "author",
            "tags",
        ),
        ("text",),
        ("image",),
    )
    raw_id_fields = ("author",)
    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter = ("name", "author__username", "tags__name")

    inlines = (IngredientInline,)
    save_on_top = True
    empty_value_display = "-пусто-"

    @admin.display(description="Фотография")
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    @admin.display(description="В избранном")
    def count_favorites(self, obj):
        return obj.recipes_favorite_related.count()

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj):
        return ", ".join(
            ingredient.name for ingredient in obj.ingredients.all())

    list_display_links = ("name", "author")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"

    save_on_top = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    empty_value_display = "-пусто-"
    search_fields = ("name", "color")
    list_display_links = ("name", "color")
    save_on_top = True


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"
    list_display_links = ("user", "recipe")
    save_on_top = True


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
        "date_added",
    )
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"
    list_display_links = ("user", "recipe")
    save_on_top = True


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
    empty_value_display = "-пусто-"
    list_display_links = ("recipe", "ingredient")
    save_on_top = True
