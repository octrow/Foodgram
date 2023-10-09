import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import AuthorFilterMixin
from api.paginations import CustomPagination
from api.permissions import AuthorAdminOrReadOnly
from api.serializers import (
    FavoriteCreateDeleteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingCartCreateDeleteSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import CustomUser, Subscription


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author_id = self.kwargs.get("id")  # ждёт тестов
        author = get_object_or_404(CustomUser, id=author_id)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if request.method == "POST":
            if subscription.exists():
                return Response(
                    {"error": "Вы уже подписаны на этого человека"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.user == author:
                return Response(
                    {"errors": "Нельзя подписаться на себя самого"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = SubscribeSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = CustomUser.objects.filter(
            subscribers__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class RecipeViewSet(AuthorFilterMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AuthorAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def post_or_delete(self, pk, serializer_class):
        user = self.request.user
        if self.request.method == "POST":
            if not Recipe.objects.filter(id=pk).exists():
                return Response(
                    {"error": "Рецепт не найден"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recipe = get_object_or_404(Recipe, pk=pk)
            if serializer_class.Meta.model.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer_class(
                data={"user": user.id, "recipe": pk},
                context={"request": self.request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            recipe = get_object_or_404(Recipe, pk=pk)
            object = serializer_class.Meta.model.objects.filter(
                user=user, recipe=recipe
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
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.post_or_delete(pk, FavoriteCreateDeleteSerializer)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self.post_or_delete(pk, ShoppingCartCreateDeleteSerializer)

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = (
            AmountIngredient.objects.select_related("recipe", "ingredient")
            .filter(recipe__shopping_cart__user=request.user)
            .values_list(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        buffer = io.StringIO()
        buffer.write(
            "\n".join("\t".join(map(str, item)) for item in shopping_cart)
        )
        response = FileResponse(buffer.getvalue(), content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
