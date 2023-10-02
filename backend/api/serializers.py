import base64
# from colorfield.serializers import ColorField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError  # убрать?

from api.mixins import IsFavoritedMixin, IsInShoppingCartMixin
from core.functions import (
    cache_get_or_set,
    get_ingredients_dict,
    get_tags_list,
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


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)

class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(user=user).exists()
        # return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = tuple(CustomUser.REQUIRED_FIELDS) + (
            CustomUser.USERNAME_FIELD,
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = ("__all__",)

    # def validate(self, data):
    #     for field, value in data.items():
    #         value = value.strip(" #")
    #         value = value.upper()
    #         data[field] = value
    #     return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class AmountIngredientSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(
    #     source="ingredient.id", read_only=True
    # )
    id = serializers.PrimaryKeyRelatedField(source='ingredient', read_only=True)
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField(min_value=0.01, validators=[MinValueValidator(0.01)])

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "name",
            "amount",
            "measurement_unit",
        )
class FavoriteCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("recipe",)

    def validate(self, data):
        user = self.context.get("request").user
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в избранное."
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

class SubscribeSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = (
            self.context.get("request").parser_context.get("kwargs").get("id")
        )
        try:
            author = CustomUser.objects.get(id=author_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                detail="Автор не найден",
                code=status.HTTP_400_BAD_REQUEST,
            )
        user = self.context.get("request").user
        if user.follower.filter(author=author_id).exists():
            raise serializers.ValidationError(
                detail="Подписка уже существует",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail="Нельзя подписаться на самого себя",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True, read_only=True).data





# class FavoriteListSerializer(RecipeListAPIView):
#     def get_queryset(self):
#         user = self.request.user
#         return Recipe.objects.filter(favorites__user=user)

# class ShoppingCartListSerializer(RecipeListAPIView):
#     def get_queryset(self):
#         user = self.request.user
#         return Recipe.objects.filter(shopping_list__user=user)


class ShoppingCartCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("recipe",)

    def validate(self, data):
        user = self.context.get("request").user
        if user.shopping_list.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже добавлен в корзину")
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

class BaseRecipeSerializer(serializers.ModelSerializer, IsFavoritedMixin, IsInShoppingCartMixin):
    ingredients = AmountIngredientSerializer(source='recipe_ingredient', many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

class RecipeReadSerializer(BaseRecipeSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

class RecipeCreateSerializer(BaseRecipeSerializer):
    image = Base64ImageField()
    ingredients = AmountIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cooking_time = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Отсутствуют ингридиенты')
        ids = set()
        for item in value:
            if not isinstance(item, dict) or 'id' not in item or 'amount' not in item:
                raise serializers.ValidationError('Неверный формат данных ингредиентов')
            if not isinstance(item['id'], int) or not isinstance(item['amount'], int):
                raise serializers.ValidationError('Неверный тип данных ингредиентов')
            if item['id'] <= 0 or item['amount'] <= 0:
                raise serializers.ValidationError('Неверное значение данных ингредиентов')
            if item['id'] in ids:
                raise serializers.ValidationError('Ингридиенты должны быть уникальны')
            ids.add(item['id'])
        return value

    def create_ingredients(self, obj, value):
        items = []
        for item in value:
            ingredient_id = item['id']
            amount = item['amount']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            items.append(AmountIngredient(ingredient=ingredient, amount=amount, recipe=obj))
        AmountIngredient.objects.bulk_create(items)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user or None
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.clear()
        AmountIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(tags_data)
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

class RecipeShortSerializer(BaseRecipeSerializer):
    image = Base64ImageField(read_only=True) # ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# class RecipeListAPIView(generics.ListAPIView):
#     serializer_class = RecipeShortSerializer
#
#     def get_queryset(self):
#         return Recipe.objects.all()



# class RecipeShortSerializer(serializers.ModelSerializer):
#     image = Base64ImageField()
#
#     class Meta:
#         model = Recipe
#         fields = ("id", "name", "image", "cooking_time")
#         read_only_fields = ("__all__",)



# class RecipeReadSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     author = CustomUserSerializer(many=False)
#     ingredients = AmountIngredientSerializer(
#         many=True, source="recipe_ingredient"
#     )
#     is_favorited = (
#         serializers.SerializerMethodField()
#     )  # аннотации и префетчинг для оптимизации
#     is_in_shopping_cart = (
#         serializers.SerializerMethodField()
#     )  # аннотации и префетчинг для оптимизации
#     image = Base64ImageField()
#
#     class Meta:
#         model = Recipe
#         fields = (
#             "id",
#             "tags",
#             "author",
#             "ingredients",
#             "is_favorited",
#             "is_in_shopping_cart",
#             "name",
#             "image",
#             "text",
#             "cooking_time",
#         )
#         read_only_fields = (
#             "author",
#             "tags" "is_favorite",
#             "is_shopping_cart",
#         )
#         exclude = ('favorites',)
#
#     # def get_ingredients(self, obj):
#     #     ingredients = obj.ingredients.values(
#     #         "id",
#     #         "name",
#     #         "measurement_unit",
#     #         amount=F("recipe_ingredient__amount"),  # поменять имя
#     #     )
#     #     return ingredients
#
#     def get_is_favorited(self, obj):  # аннотации и префетчинг для оптимизации
#         request = self.context.get("request")
#         if not request or request.user.is_anonymous:
#             return False
#         return obj.favorites.filter(user=request.user).exists()
#
#     def get_is_in_shopping_cart(
#             self, obj
#     ):  # аннотации и префетчинг для оптимизации
#         request = self.context.get("request")
#         if not request or request.user.is_anonymous:
#             return False
#         return obj.shopping_list.filter(user=request.user).exists()


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True
#     )
#     author = CustomUserSerializer(read_only=True)
#     # ingredients = serializers.ListField(child=serializers.JSONField())
#     ingredients = AmountIngredientSerializer(
#         many=True,
#     )
#     image = Base64ImageField()
#
#     class Meta:
#         model = Recipe
#         fields = (
#             "id",
#             "tags",
#             "author",
#             "ingredients",
#             "name",
#             "image",
#             "text",
#             "cooking_time",
#         )
#
#     def validate_ingredients(self, value):
#         if not isinstance(
#                 value, list
#         ):  # serializers.PrimaryKeyRelatedField и AmountIngredientSerializer уже валидируют, что входные данные являются списком
#             raise serializers.ValidationError(
#                 "Входные данные должны быть списком."
#             )
#         ingredients = value
#         if not ingredients:
#             raise serializers.ValidationError("Отсутствуют ингридиенты.")
#         ingredient_ids = [ingredient["id"] for ingredient in ingredients]
#         if len(ingredient_ids) != len(set(ingredient_ids)):
#             raise serializers.ValidationError(
#                 "Ингридиенты должны быть уникальны."
#             )
#         for ingredient in ingredients:
#             if int(ingredient["amount"]) <= 0:
#                 raise serializers.ValidationError(
#                     "Количество ингредиента должно быть больше 0"
#                 )
#             if not Ingredient.objects.filter(id=ingredient["id"]).exists():
#                 raise serializers.ValidationError(
#                     f'Ингридиент с id {ingredient["id"]} не существует.'
#                 )
#         return value
#
#     # @staticmethod
#     # def link_ingredients(
#     #     recipe, ingredients
#     # ):  # неэффективно? метод bulk_create для создания нескольких объектов AmountIngredient за один запрос
#     #     for ingredient_data in ingredients:
#     #         AmountIngredient.objects.create(
#     #             ingredient=ingredient_data.pop("id"),
#     #             amount=ingredient_data.pop("amount"),
#     #             recipe=recipe,
#     #         )
#
#     def validate_tags(self, value: list) -> list:
#         if not isinstance(
#                 value, list
#         ):  # serializers.PrimaryKeyRelatedField и AmountIngredientSerializer уже валидируют, что входные данные являются списком
#             raise serializers.ValidationError(
#                 "Входные данные должны быть списком."
#             )
#         tags = value
#         if not tags:
#             raise serializers.ValidationError(
#                 "The recipe must have at least one tag."
#             )
#         for tag in tags:
#             if not Tag.objects.filter(id=tag.id).exists():
#                 raise serializers.ValidationError(
#                     {"tags": f"Указанного тега {tag} не существует"}
#                 )
#         return value
#
#     def validate_cooking_time(
#             self, cooking_time
#     ):  # избыточно?PositiveSmallIntegerField
#         if cooking_time < 1:
#             raise serializers.ValidationError(
#                 {
#                     "cooking_time": "Время готовки должно быть не меньше одной минуты"
#                 }
#             )
#         return cooking_time
#
#     @transaction.atomic
#     def create(self, validated_data):
#         tags = validated_data.pop("tags")
#         ingredients_data = validated_data.pop("ingredients")
#         author = self.context.get("request").user
#         recipe = Recipe.objects.create(author=author, **validated_data)
#         # Оптимизация: использование кэширования для хранения списка тегов
#         # Получить список тегов из кэша или из базы данных с помощью функции cache_get_or_set
#         tags_list = cache_get_or_set(
#             "Tag", tags, get_tags_list
#         )  ## !использовать сигналы или другие механизмы для обновления кэша
#         # Установить связь между рецептом и тегами по списку тегов
#         if tags_list:
#             recipe.tags.set(tags_list)
#         # Оптимизация: использование метода bulk_create для создания нескольких объектов модели AmountIngredient за один запрос
#         # Собрать список объектов модели AmountIngredient из цикла по списку ингредиентов
#         amount_ingredient_list = []
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data["id"]
#             amount = ingredient_data["amount"]
#             # Получить словарь с ингредиентами из кэша или из базы данных с помощью функции cache_get_or_set
#             ingredients_dict = cache_get_or_set(
#                 "Ingredient", [ingredient_id], get_ingredients_dict
#             )
#             # Проверить на существование ключа в словаре перед обращением к нему
#             if ingredient_id in ingredients_dict:
#                 ingredient = ingredients_dict[ingredient_id]
#                 amount_ingredient_list.append(
#                     AmountIngredient(
#                         recipe=recipe,
#                         ingredient=ingredient,
#                         amount=amount,
#                     )
#                 )
#         # Создать связи между рецептом и ингредиентами по списку объектов модели AmountIngredient
#         if amount_ingredient_list:
#             AmountIngredient.objects.bulk_create(amount_ingredient_list)
#         return recipe
#
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         tags = validated_data.pop("tags")
#         ingredients_data = validated_data.pop("ingredients")
#         # Оптимизация: использование кэширования для хранения списка тегов
#         # Получить список тегов из кэша или из базы данных с помощью функции cache_get_or_set
#         tags_list = cache_get_or_set("Tag", tags, get_tags_list)
#         # Проверить на пустоту список тегов перед использованием метода set
#         if tags_list:
#             # Установить связь между рецептом и тегами по списку тегов
#             instance.tags.set(tags_list)
#         # Удалить все связи между рецептом и ингредиентами
#         instance.recipe_ingredient.all().delete()
#         # Оптимизация: использование метода bulk_create для создания нескольких объектов модели AmountIngredient за один запрос
#         # Собрать список объектов модели AmountIngredient из цикла по списку ингредиентов
#         amount_ingredient_list = []
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data["id"]
#             amount = ingredient_data["amount"]
#             # Получить словарь с ингредиентами из кэша или из базы данных с помощью функции cache_get_or_set
#             ingredients_dict = cache_get_or_set(
#                 "Ingredient", [ingredient_id], get_ingredients_dict
#             )
#             # Проверить на существование ключа в словаре перед обращением к нему
#             if ingredient_id in ingredients_dict:
#                 # Проверить на тип данных, возвращаемых функцией cache_get_or_set
#                 if isinstance(ingredients_dict, dict):
#                     ingredient = ingredients_dict[ingredient_id]
#                     amount_ingredient_list.append(
#                         AmountIngredient(
#                             recipe=instance,
#                             ingredient=ingredient,
#                             amount=amount,
#                         )
#                     )
#         # Создать связи между рецептом и ингредиентами по списку объектов модели AmountIngredient
#         if amount_ingredient_list:
#             AmountIngredient.objects.bulk_create(amount_ingredient_list)
#         return super().update(instance, validated_data)
#
#     @transaction.atomic
#     def create_ingredients_amounts(self, ingredients, recipe):
#         # Проверяем, что список ингредиентов не пустой
#         if not ingredients:
#             # Возвращаем None или пустой список, если список пустой
#             return None
#         # Оптимизируем количество запросов к базе данных
#         # Получаем все ингредиенты по списку id за один запрос с помощью метода in_bulk
#         ingredients_dict = Ingredient.objects.in_bulk(
#             [ingredient["id"] for ingredient in ingredients]
#         )
#         # Собираем список объектов модели AmountIngredient из цикла по списку ингредиентов
#         amount_ingredient_list = []
#         for ingredient in ingredients:
#             # Проверяем, что ингредиенты существуют в базе данных
#             try:
#                 # Получаем ингредиент по id из словаря ингредиентов
#                 ingredient_obj = ingredients_dict[ingredient["id"]]
#             except KeyError:
#                 # Возбуждаем исключение, если ингредиент с таким id не найден
#                 raise Ingredient.DoesNotExist(
#                     f'Ingredient with id {ingredient["id"]} does not exist.'
#                 )
#             # Проверяем, что количество каждого ингредиента положительное
#             try:
#                 # Приводим количество к абсолютному значению с помощью функции abs
#                 amount = abs(ingredient["amount"])
#                 # Возбуждаем исключение, если количество равно нулю
#                 if amount == 0:
#                     raise serializers.ValidationError(
#                         "The amount of each ingredient must be positive."
#                     )
#             except (TypeError, ValueError):
#                 # Возбуждаем исключение, если количество не является числом или не может быть приведено к числу
#                 raise ValidationError(
#                     "The amount of each ingredient must be a number."
#                 )
#             # Добавляем объект модели AmountIngredient в список
#             amount_ingredient_list.append(
#                 AmountIngredient(
#                     ingredient=ingredient_obj, recipe=recipe, amount=amount
#                 )
#             )
#         # Создаем связи между рецептом и ингредиентами по списку объектов модели AmountIngredient с помощью метода bulk_create
#         AmountIngredient.objects.bulk_create(amount_ingredient_list)
#
#     def to_representation(self, instance: Recipe) -> dict:
#         context = {"request": self.context.get("request")}
#         return RecipeReadSerializer(instance, context=context).data
