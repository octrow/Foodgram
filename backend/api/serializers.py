from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from api.mixins import IsFavoritedMixin, IsInShoppingCartMixin
from recipes.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.subscriptions.filter(user=user, author=obj).exists()
        return False


class SubscribeSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].GET.get("recipes_limit")
        if recipes_limit:
            return RecipeShortSerializer(
                Recipe.objects.filter(author=obj)[: int(recipes_limit)],
                many=True,
            ).data
        return RecipeShortSerializer(
            Recipe.objects.filter(author=obj), many=True
        ).data


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9]+([_.-]?[a-zA-Z0-9])*$",
                (
                    "Юзернейм может содержать только цифры, латинские буквы,"
                    " знаки (не в начале): тире, точка и нижнее тире."
                ),
            )
        ]
    )

    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class CreateAmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        fields = ("id", "amount")
        model = AmountIngredient


class BaseRecipeSerializer(
    serializers.ModelSerializer, IsFavoritedMixin, IsInShoppingCartMixin
):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = AmountIngredientSerializer(
        many=True,
        source="recipe_ingredient",
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeReadSerializer(BaseRecipeSerializer):
    image = Base64ImageField()

    class Meta(BaseRecipeSerializer.Meta):
        pass


class RecipeCreateSerializer(BaseRecipeSerializer):
    image = Base64ImageField()
    ingredients = CreateAmountIngredientSerializer(many=True, write_only=True)
    tags = serializers.SlugRelatedField(
        slug_field="id", queryset=Tag.objects.all(), many=True
    )

    class Meta(BaseRecipeSerializer.Meta):
        pass

    def validate(self, validated_data):
        if len(validated_data.get("name")) > 150:
            raise serializers.ValidationError(
                {"name": "Название должно быть короче 150 символов!"}
            )
        if validated_data.get("cooking_time") < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не меньше 1 минуты!"
            )
        if not self.instance and not validated_data.get("image"):
            raise serializers.ValidationError(
                {"image": "Поле изображения не может быть пустым!"}
            )
        ingredients = validated_data.get("ingredients")
        if not ingredients or len(ingredients) == 0:
            raise serializers.ValidationError(
                {"ingredients": "Поле ингредиентов не может быть пустым!"}
            )
        ingredient_ids = set(
            ingredient.get("id") for ingredient in ingredients
        )
        if len(ingredient_ids) != len(ingredients):
            raise serializers.ValidationError(
                {"ingredients": "Ингридиенты не должны повторяться!"}
            )
        if Ingredient.objects.filter(id__in=ingredient_ids).count() != len(
            ingredients
        ):
            raise serializers.ValidationError(
                {"ingredients": "Некоторые ингридиенты не существуют!"}
            )
        tags = validated_data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Поле тегов не может быть пустым!"}
            )
        tags_ids = set(tag.id for tag in tags)
        if len(tags_ids) != len(tags):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться!"}
            )
        return validated_data

    @transaction.atomic
    def create_ingredients(self, recipe, ingredients):
        ingredient_counts = {
            ingredient["id"]: ingredient["amount"]
            for ingredient in ingredients
        }
        create_ingredients = [
            AmountIngredient(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount
            )
            for ingredient_id, amount in ingredient_counts.items()
        ]
        AmountIngredient.objects.bulk_create(create_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        current_user = self.context["request"].user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data, author=current_user)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        if validated_data.get("image") is not None:
            instance.image = validated_data.pop("image")
        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        if (
            instance.image is not None
            and validated_data.get("image") is not None
        ):
            instance.image.delete()
        return instance

    def to_representation(self, recipe):
        context = {"request": self.context.get("request")}
        return RecipeReadSerializer(recipe, context=context).data


class RecipeShortSerializer(BaseRecipeSerializer):
    image = Base64ImageField()

    class Meta(BaseRecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, data):
        user = self.context.get("request").user
        recipe = data["recipe"]
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже добавлен")
        return data

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context
        )
        return serializer.data


class FavoriteCreateDeleteSerializer(ShoppingCartCreateDeleteSerializer):
    class Meta:
        model = Favorite
        fields = (
            "user",
            "recipe",
        )
