"""Модуль для импорта данных из CSV-файла с ингридиентами."""

from csv import reader
from django.core.management import BaseCommand
import os
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка данных из csv в базу данных."""

    help = 'Load data from csv files to database'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'ingredients.csv')

        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = reader(csv_file)
            for row in csv_reader:
                Ingredient.objects.update_or_create(
                    name=row[0].strip(),
                    measure=row[1].strip()
                )
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
