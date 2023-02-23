import csv
from django.core.management import BaseCommand
from recipes.models import Ingredient


PATH = "/recipes/data/"


class Command(BaseCommand):
    help = "import data from ingredients.csv"

    def handle(self, *args, **kwargs):

        with open(f"{PATH}ingredients.csv", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                ingredient = Ingredient(
                    id=row[0],
                    name=row[1],
                    measurement_unit=row[2],
                )
                ingredient.save()



