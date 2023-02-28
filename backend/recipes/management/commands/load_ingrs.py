import csv
import os

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from ingredients.csv to DB.'

    def handle(self, *args, **options):
        data_dir = os.path.join(BASE_DIR, 'recipes', 'data')
        with open(
                os.path.join(data_dir, 'ingredients.csv'),
                encoding='utf-8'
        ) as csv_file:
            for row in csv.reader(csv_file):
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
