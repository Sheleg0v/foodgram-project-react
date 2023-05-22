import csv

from django.core.management.base import BaseCommand

from django.conf import settings
from recipes.models import Ingredient
from users.models import User


FILE_PATH: int = 0
MODEL_NAME: int = 1


class Command(BaseCommand):
    help = (
        'Add ingredients to database from csv file.'
        'usage: python manage.py importcsv path'
    )

    def add_arguments(self, parser):
        parser.add_argument('file_path')

    def handle(self, *args, **options):
        file_path = options.get('file_path')
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for name, measurement_unit in reader:
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
