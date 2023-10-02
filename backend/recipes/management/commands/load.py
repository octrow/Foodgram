import json
from foodgram import settings

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = " Загрузить данные в модель ингредиентов "

    def load_data(self, file_name, model):
        with open(
            f"{settings.BASE_DIR}/{file_name}", encoding="utf-8"
        ) as data_file:
            data = json.load(data_file)
            for item in data:
                model.objects.get_or_create(**item)

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Старт команды"))
        files_and_models = [
            ("data/ingredients.json", Ingredient),
            ("data/tags.json", Tag),
        ]
        for file_name, model in files_and_models:
            self.load_data(file_name, model)
        self.stdout.write(self.style.SUCCESS("Данные загружены"))
