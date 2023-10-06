from django.contrib import admin
from django.contrib.admin import display
from django.utils.safestring import mark_safe

from .models import (AmountIngredient, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)

admin.site.site_header = "Администрирование Foodgram"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_image",
        # "added_in_favorites"
    )
    # readonly_fields = ("added_in_favorites",)
    list_filter = (
        "author",
        "name",
        "tags",
    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = "Изображение"

    @display(description="Количество в избранных")
    def added_in_favorites(self, obj):
        return obj.favorites.count()

    added_in_favorites.short_description = "В избранном"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
