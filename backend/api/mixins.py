from rest_framework import serializers


class IsInUserFieldMixin:
    def get_is_in_user_field(self, obj, field):
        user = self.context.get("request").user
        if user.is_authenticated:
            return getattr(user, field).filter(recipe=obj).exists()
        return False


class IsFavoritedMixin(IsInUserFieldMixin):
    is_favorited = serializers.BooleanField(read_only=True)

    def get_is_favorited(self, obj):
        return self.get_is_in_user_field(obj, "favorite")


class IsInShoppingCartMixin:
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_in_user_field(obj, "shopping_cart")


class AuthorFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author=author)
        return queryset
