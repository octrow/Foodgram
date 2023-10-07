from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from core.texts import EMPTY_VALUE_DISPLAY


admin.site.site_header = "Администрирование Foodgram"


class IngredientInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_image",
        "cooking_time",
        "count_favorites",
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
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = "Фотография"

    def count_favorites(self, obj):
        return obj.favorite.count()

    count_favorites.short_description = "В избранном"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = EMPTY_VALUE_DISPLAY

    save_on_top = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    empty_value_display = EMPTY_VALUE_DISPLAY
    search_fields = ("name", "color")

    save_on_top = True


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user__username", "recipe__name")
    empty_value_display = EMPTY_VALUE_DISPLAY

    save_on_top = True


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
        "date_added",
    )
    search_fields = ("user__username", "recipe__name")
    empty_value_display = EMPTY_VALUE_DISPLAY

    save_on_top = True


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
    empty_value_display = EMPTY_VALUE_DISPLAY

    save_on_top = True
