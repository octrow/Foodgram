from django.test import TestCase

from backend.recipes.management.commands.load import Command
from backend.recipes.models import Ingredient, Recipe


class NewBusinessLogicTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            name="Test Recipe", description="Test Description"
        )
        self.ingredient = Ingredient.objects.create(
            name="Test Ingredient", measurement_unit="g"
        )

    def test_load_command(self):
        command = Command()
        command.handle()
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Ingredient.objects.count(), 1)

    def test_recipe_creation(self):
        Recipe.objects.create(name="New Recipe", description="New Description")
        self.assertEqual(Recipe.objects.count(), 2)

    def test_ingredient_creation(self):
        Ingredient.objects.create(name="New Ingredient", measurement_unit="kg")
        self.assertEqual(Ingredient.objects.count(), 2)
