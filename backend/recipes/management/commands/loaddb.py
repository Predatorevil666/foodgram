import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


def ingredients_create(rows):
    ingredients = []
    for row in rows:
        ingredients.append(Ingredient(
            name=row[0],
            measurement_unit=row[1]
        ))
    Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)


def tags_create(rows):
    tags = []
    for row in rows:
        tags.append(Tag(
            name=row[0],
            slug=row[2]
        ))
    Tag.objects.bulk_create(tags, ignore_conflicts=True)


action = {
    'ingredients.csv': ingredients_create,
    'tags.csv': tags_create,
}


class Command(BaseCommand):
    help = "Загрузить ингредиенты в БД из CSV"

    def handle(self, *args, **options):
        for filename, func in action.items():
            path = os.path.join(settings.BASE_DIR, "data/", filename)
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                func(list(reader))
        self.stdout.write("!!!База данных загружена успешно!!!")
