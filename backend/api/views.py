import io
from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from djoser.views import UserViewSet

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from api.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from recipes.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import CustomUser, Subscription

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination

from .permissions import AuthorAdminOrReadOnly


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CustomUserSerializer
    search_fields = ["username", "email"]
    pagination_class = CustomPagination

    # Добавить GET http://localhost/api/users/me/ Текущий пользователь
    # application/json
    # {
    #     "email": "user@example.com",
    #     "id": 0,
    #     "username": "string",
    #     "first_name": "Вася",
    #     "last_name": "Пупкин",
    #     "is_subscribed": false
    # }



    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Создание и удаление связи между пользователями."""

        user = request.user
        try:
            author_id = int(self.kwargs.get('id'))
        except (TypeError, ValueError):
            return Response({'error': 'Неверный формат id'}, status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(CustomUser, id=author_id)
        if request.method == 'POST':
            if user == author:
                return Response({'error': 'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(author, data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.get_or_create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscription, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список подписок пользоваетеля."""

        queryset = CustomUser.objects.filter(subscribers__user=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Обработка запросов на получение ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    # search_fields = ["name", "measurement_unit"]


class TagViewSet(ReadOnlyModelViewSet):
    """Обработка запросов на получение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    pagination_class = None
    # filter_backends = [filters.SearchFilter]


class RecipeViewSet(ModelViewSet):
    """Работа с рецептами.
    Обработка запросов CRUD рецептов
    Добавление и удаление рецепта в избранное/корзину покупок"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["favorite", "shopping_cart"]:
            return RecipeShortSerializer
        elif self.request.method in ["GET"]:
            return RecipeReadSerializer
        else:
            return RecipeCreateSerializer

    def add_to(self, model, user, recipe_id):
        """Добавляет рецепт в модель (избранное или корзину)."""
        recipe = self.get_recipe_by_id(recipe_id)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Рецепт уже добавлен"}, status=status.HTTP_400_BAD_REQUEST)

    def delete_from(self, model, user, recipe_id):
        """Удаляет рецепт из модели (избранного или корзины)."""
        recipe = self.get_recipe_by_id(recipe_id)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_recipe_by_id(self, recipe_id):
        """Возвращает объект рецепта по id или возвращает ошибку 400."""
        try:
            recipe_id = int(recipe_id)
        except (TypeError, ValueError):
            return Response({"error": "Неверный формат id"}, status=status.HTTP_400_BAD_REQUEST)
        return get_object_or_404(Recipe, id=recipe_id)

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""
        if request.method == "POST":
            return self.add_to(Favorite, request.user, pk)
        elif request.method == "DELETE":
            return self.delete_from(Favorite, request.user, pk)

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из корзины."""
        if request.method == "POST":
            return self.add_to(ShoppingCart, request.user, pk)
        elif request.method == "DELETE":
            return self.delete_from(ShoppingCart, request.user, pk)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Генерирует и отправляет PDF-файл со списком покупок."""
        ingredients = self.get_ingredients_from_shopping_cart(request.user)
        if not ingredients:
            return Response({"error": "Список покупок пуст"}, status=status.HTTP_404_NOT_FOUND)
        try:
            pdf = self.generate_pdf_file(ingredients)
        except Exception as e:
            return Response({"error": f"Ошибка при генерации PDF-файла: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        # response = FileResponse(pdf, as_attachment=True, filename="shopping_cart.pdf")
        return response

    def get_ingredients_from_shopping_cart(self, user):
        """Возвращает QuerySet с ингредиентами из корзины пользователя."""
        return (
            Recipe.objects.filter(shopping_cart__user=user)
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(amount=Sum("ingredients__amount"))
            .order_by("ingredients__name")
        )

    def generate_pdf_file(self, ingredients):
        """Возвращает буфер с PDF-данными с списком ингредиентов."""
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        x = 50
        y = 750
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(x, y, "Список покупок")
        y -= 20
        pdf.setFont("Helvetica", 12)
        pdf.drawString(x, y, f"Дата: {timezone.now().strftime('%d.%m.%Y')}")
        y -= 20
        data = [["Название", "Количество", "Единица измерения"]]
        for ingredient in ingredients:
            data.append(
                [ingredient["ingredients__name"], ingredient["amount"], ingredient["ingredients__measurement_unit"]])
        table = Table(data, colWidths=[200, 100, 100])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        table.wrapOn(pdf, x, y)
        table.drawOn(pdf, x, y - table._height)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer
