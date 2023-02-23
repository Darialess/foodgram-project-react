import json
import os

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from ingredients.json to DB.'

    def handle(self, *args, **options):
        data_dir = os.path.join(BASE_DIR, 'recipes', 'data')
        with open(
                os.path.join(data_dir, 'ingredients.json'),
                encoding='utf-8'
        ) as json_file:
            data = json.load(json_file)

        for item in data:
            Ingredient.objects.get_or_create(
                name=item.get('name'),
                measurement_unit=item.get('measurement_unit')
            )