from rest_framework import serializers


class IsFavoritedMixin:
    is_favorited = serializers.BooleanField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorite.filter(recipe=obj).exists()
        return False

class IsInShoppingCartMixin:
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False