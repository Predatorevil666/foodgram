import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


def ingredients_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1],
    )


def tags_create(row):
    Tag.objects.get_or_create(
        name=row[0],
        color=row[1],
        slug=row[2],
    )


action = {
    'ingredients.csv': ingredients_create,
    'tags.csv': tags_create,
}


class Command(BaseCommand):
    help = "Загрузить ингредиенты в БД из CSV"

    def handle(self, *args, **options):
        for filename, func in action.items():
            path = os.path.join(settings.BASE_DIR, "data/") + filename
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    func(row)
        self.stdout.write("!!!База данных загружена успешно!!!")
