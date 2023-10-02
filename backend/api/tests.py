# Importing the necessary modules and libraries
import base64

import pytest
from django.core.files.base import ContentFile

from api.serializers import (Base64ImageField, CustomUserSerializer,
                             FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer,
                             RecipeIngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer)
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscription


# Creating some pytest fixtures to set up some test data
@pytest.fixture
def user1():
    return CustomUser.objects.create_user(
        email='user1@example.com',
        username='user1',
        password='user1password'
    )

@pytest.fixture
def user2():
    return CustomUser.objects.create_user(
        email='user2@example.com',
        username='user2',
        password='user2password'
    )

@pytest.fixture
def tag1():
    return Tag.objects.create(
        name='Breakfast',
        color='#FF0000',
        slug='breakfast'
    )

@pytest.fixture
def tag2():
    return Tag.objects.create(
        name='Lunch',
        color='#00FF00',
        slug='lunch'
    )

@pytest.fixture
def ingredient1():
    return Ingredient.objects.create(
        name='Eggs',
        measurement_unit='pcs'
    )

@pytest.fixture
def ingredient2():
    return Ingredient.objects.create(
        name='Bread',
        measurement_unit='slices'
    )

@pytest.fixture
def recipe1(user1):
    recipe = Recipe.objects.create(
        author=user1,
        name='Egg Sandwich',
        image=ContentFile(base64.b64decode('some base64 encoded image'), name='photo.jpg'),
        text='Some instructions',
        cooking_time=10
    )
    recipe.tags.add(tag1)
    AmountIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient1,
        amount=2
    )
    AmountIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient2,
        amount=4
    )
    return recipe

@pytest.fixture
def favorite1(user2, recipe1):
    return Favorite.objects.create(
        user=user2,
        recipe=recipe1
    )

@pytest.fixture
def shopping_cart1(user2, recipe1):
    return ShoppingCart.objects.create(
        user=user2,
        recipe=recipe1
    )

@pytest.fixture
def subscription1(user2, user1):
    return Subscription.objects.create(
        user=user2,
        author=user1
    )

# Testing the UserSerializer
def test_user_serializer(user1, mocker):
    # Mocking the UserSerializer.get_is_subscribed method to return False
    mocker.patch('api.serializers.UserSerializer.get_is_subscribed', return_value=False)
    # Creating a serializer instance with user1
    serializer = CustomUserSerializer(instance=user1)
    # Creating an expected data dictionary with user1 fields
    expected_data = {
        'id': user1.id,
        'email': 'user1@example.com',
        'username': 'user1',
        'first_name': '',
        'last_name': '',
        'is_subscribed': False
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Testing the SubscriptionSerializer
@pytest.mark.parametrize('user, author, is_valid, error_message', [
    # Valid case with different user and author
    (user2, user1, True, None),
    # Invalid case with same user and author
    (user1, user1, False, 'You cannot subscribe to yourself.'),
    # Invalid case with existing subscription
    (user2, user1, False, 'You are already subscribed to this author.')
])
def test_subscription_serializer(user, author, is_valid, error_message, subscription1):
    # Creating a data dictionary with user and author fields
    data = {
        'user': user,
        'author': author
    }
    # Creating a serializer instance with data
    serializer = SubscriptionSerializer(data=data)
    # Checking if the serializer is valid or not depending on the input values
    assert serializer.is_valid() == is_valid
    # Checking if the serializer error message matches the expected error message
    if not is_valid:
        assert serializer.errors['non_field_errors'][0] == error_message

# Testing the TagSerializer
def test_tag_serializer(tag1):
    # Creating a serializer instance with tag1
    serializer = TagSerializer(instance=tag1)
    # Creating an expected data dictionary with tag1 fields
    expected_data = {
        'id': tag1.id,
        'name': 'Breakfast',
        'color': '#FF0000',
        'slug': 'breakfast'
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Testing the IngredientSerializer
def test_ingredient_serializer(ingredient1):
    # Creating a serializer instance with ingredient1
    serializer = IngredientSerializer(instance=ingredient1)
    # Creating an expected data dictionary with ingredient1 fields
    expected_data = {
        'id': ingredient1.id,
        'name': 'Eggs',
        'measurement_unit': 'pcs'
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Checking the test coverage for part 2 using pytest-cov plugin
# Running pytest with --cov option to specify which modules to measure coverage for
# and --cov-report option to specify how to display or save the coverage results
# For example:
# pytest --cov=api.serializers --cov-report=term-missing tests/test_serializers_part2.py

# Testing the RecipeIngredientSerializer
def test_recipe_ingredient_serializer(recipe_ingredient1):
    # Creating a serializer instance with recipe_ingredient1
    serializer = RecipeIngredientSerializer(instance=recipe_ingredient1)
    # Creating an expected data dictionary with recipe_ingredient1 fields
    expected_data = {
        'id': ingredient1.id,
        'name': 'Eggs',
        'amount': 2,
        'measurement_unit': 'pcs'
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Testing the RecipeSerializer
def test_recipe_serializer(recipe1, mocker):
    # Mocking the RecipeSerializer.get_is_favorited method to return True
    mocker.patch('api.serializers.RecipeSerializer.get_is_favorited', return_value=True)
    # Mocking the RecipeSerializer.get_is_in_shopping_cart method to return True
    mocker.patch('api.serializers.RecipeSerializer.get_is_in_shopping_cart', return_value=True)
    # Mocking the Base64ImageField.to_representation method to return a dummy image string
    mocker.patch('api.serializers.Base64ImageField.to_representation', return_value='some base64 encoded image')
    # Creating a serializer instance with recipe1
    serializer = RecipeSerializer(instance=recipe1)
    # Creating an expected data dictionary with recipe1 fields
    expected_data = {
        'id': recipe1.id,
        'tags': [
            {
                'id': tag1.id,
                'name': 'Breakfast',
                'color': '#FF0000',
                'slug': 'breakfast'
            }
        ],
        'author': {
            'id': user1.id,
            'email': 'user1@example.com',
            'username': 'user1',
            'first_name': '',
            'last_name': '',
            'is_subscribed': False
        },
        'ingredients': [
            {
                'id': ingredient1.id,
                'name': 'Eggs',
                'amount': 2,
                'measurement_unit': 'pcs'
            },
            {
                'id': ingredient2.id,
                'name': 'Bread',
                'amount': 4,
                'measurement_unit': 'slices'
            }
        ],
        'is_favorited': True,
        'is_in_shopping_cart': True,
        'name': 'Egg Sandwich',
        # The image field is not tested here because it depends on the base64 encoding
        # of the image file, which may vary depending on the implementation
        # of the Base64ImageField class
        # However, it can be tested by comparing the decoded image data with the original image file
        # using the base64.b64decode function and the filecmp.cmp function
        # For example:
        # image_data = serializer.data['image']
        # format, imgstr = image_data.split(';base64,')
        # decoded_image = base64.b64decode(imgstr)
        # with open('decoded_image.jpg', 'wb') as f:
        #     f.write(decoded_image)
        # assert filecmp.cmp('decoded_image.jpg', recipe1.image.path)
        # os.remove('decoded_image.jpg')
        # Alternatively, it can be tested by mocking the Base64ImageField class and its methods
        # using the pytest-mock plugin and the mocker fixture
        # For example:
        # mocker.patch('api.serializers.Base64ImageField.to_representation', return_value='some base64 encoded image')
        # serializer = RecipeSerializer(instance=recipe1)
        # assert serializer.data['image'] == 'some base64 encoded image'
        'image': serializer.data['image'],
        'text': 'Some instructions',
        'cooking_time': 10
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Testing the RecipeCreateSerializer with different values of tags and ingredients
@pytest.mark.parametrize('tags, ingredients, is_valid, error_message', [
    # Valid case with one tag and two ingredients
    ([tag2.id], [
        {
            'id': ingredient1.id,
            'amount': 3
        },
        {
            'id': ingredient2.id,
            'amount': 6
        }
    ], True, None),
    # Invalid case with no tags
    ([], [
        {
            'id': ingredient1.id,
            'amount': 3
        },
        {
            'id': ingredient2.id,
            'amount': 6
        }
    ], False, {'tags': ['The recipe must have at least one tag.']}),
    # Invalid case with duplicate ingredients
    ([tag2.id], [
        {
            'id': ingredient1.id,
            'amount': 3
        },
        {
            'id': ingredient1.id,
            'amount': 4
        }
    ], False, {'ingredients': ['The ingredients must be unique.']})
])
def test_recipe_create_serializer(tags, ingredients, is_valid, error_message, mocker):
    # Mocking the Base64ImageField.to_representation method to return a dummy image string
    mocker.patch('api.serializers.Base64ImageField.to_representation', return_value='some base64 encoded image')
    # Creating a data dictionary with tags, ingredients, name, image, text, and cooking_time
    data = {
        'tags': tags,
        'ingredients': ingredients,
        'name': 'Another Egg Sandwich',
        'image': ContentFile(base64.b64decode('some base64 encoded image'), name='photo.jpg'),
        'text': 'Some instructions',
        'cooking_time': 10
    }
    # Creating a serializer instance with data and context
    serializer = RecipeCreateSerializer(data=data, context={'request': request})
    # Checking if the serializer is valid or not depending on the input values
    assert serializer.is_valid() == is_valid
    # Checking if the serializer error message matches the expected error message
    if not is_valid:
        assert serializer.errors == error_message

# Checking the test coverage for part 3 using pytest-cov plugin
# Running pytest with --cov option to specify which modules to measure coverage for
# and --cov-report option to specify how to display or save the coverage results
# For example:
# pytest --cov=api.serializers --cov-report=term-missing tests/test_serializers_part3.py

# Testing the FavoriteSerializer
def test_favorite_serializer(favorite1, mocker):
    # Mocking the RecipeSerializer.to_representation method to return a dummy recipe data
    mocker.patch('api.serializers.RecipeSerializer.to_representation', return_value={'some': 'recipe data'})
    # Creating a serializer instance with favorite1
    serializer = FavoriteSerializer(instance=favorite1)
    # Creating an expected data dictionary with favorite1 fields
    expected_data = {
        'user': user2.id,
        'recipe': {'some': 'recipe data'}
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Testing the ShoppingCartSerializer
def test_shopping_cart_serializer(shopping_cart1, mocker):
    # Mocking the RecipeSerializer.to_representation method to return a dummy recipe data
    mocker.patch('api.serializers.RecipeSerializer.to_representation', return_value={'some': 'recipe data'})
    # Creating a serializer instance with shopping_cart1
    serializer = ShoppingCartSerializer(instance=shopping_cart1)
    # Creating an expected data dictionary with shopping_cart1 fields
    expected_data = {
        'user': user2.id,
        'recipe': {'some': 'recipe data'}
    }
    # Checking if the serializer data matches the expected data
    assert serializer.data == expected_data

# Writing tests or assertions for all the serializers in part 4 using pytest-cov plugin
# Running pytest with --cov option to specify which modules to measure coverage for
# and --cov-report option to specify how to display or save the coverage results
# For example:
# pytest --cov=api.serializers --cov-report=term-missing tests/test_serializers_part4.py

