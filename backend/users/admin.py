from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
    )
    list_filter = ("email", "first_name", "is_active")
    search_fields = (
        "username",
        "email",
    )
    empty_value_display = '-пусто-'

    save_on_top = True


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
    empty_value_display = '-пусто-'

    save_on_top = True
