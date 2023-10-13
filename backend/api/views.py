import io

from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (FavoriteCreateDeleteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer,
                             ShoppingCartCreateDeleteSerializer,
                             SubscribeCreateSerializer, SubscribeSerializer,
                             TagSerializer)
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        serializer = SubscribeCreateSerializer(
            data={"user": request.user.id, "author": id},
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        subscription = Subscription.objects.filter(
            user=request.user, author=id)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Вы не подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients")
    permission_classes = [AuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def create_favorite_or_shoppingcart(serializer_class, id, request):
        serializer = serializer_class(
            data={"user": request.user.id, "recipe": id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_favorite_or_shoppingcart(model, id, request):
        object = model.objects.filter(
            user=request.user, recipe_id=id
        )
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Этого рецепта нет в списке"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.create_favorite_or_shoppingcart(
            FavoriteCreateDeleteSerializer, pk, request)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        return self.delete_favorite_or_shoppingcart(
            Favorite, pk, request)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self.create_favorite_or_shoppingcart(
            ShoppingCartCreateDeleteSerializer, pk, request)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        return self.delete_favorite_or_shoppingcart(
            ShoppingCart, pk, request)

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = (
            AmountIngredient.objects.select_related("recipe", "ingredient")
            .filter(recipe__recipes_shoppingcart_related__user=request.user)
            .values_list(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        return self.create_file_response(shopping_cart)

    @staticmethod
    def create_file_response(shopping_cart):
        buffer = io.StringIO()
        buffer.write(
            "\n".join("\t".join(map(str, item)) for item in shopping_cart)
        )
        response = FileResponse(buffer.getvalue(), content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
