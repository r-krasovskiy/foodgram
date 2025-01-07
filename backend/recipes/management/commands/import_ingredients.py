"""Модуль для импорта готовой базы CSV-файла с ингридиентами."""

import os
from csv import reader

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Загрузка данных из CSV файла в базу данных.

    Загружает список ингредиентов из CSV файла в базу данных.
    Каждая строка CSV файла содержит название
    ингредиента и его единицу измерения. Если ингредиент уже существует в
    базе, его данные обновляются. В противном случае, создается новая запись.
    """

    help = 'Загрузка списка ингредиентов из csv-файла в базу данных.'

    def handle(self, *args, **options):
        """
        Чтение данных из CSV файла и их загрузка в базу данных.

        Читает файл ingredients.csv, обрабатывает каждую строку и загружает
        ингредиенты в модель Ingredient. Используется метод update_or_create,
        чтобы избежать дублирования записей.
        """
        file_path = os.path.join(
            settings.BASE_DIR, '..', 'data', 'ingredients.csv'
        )

        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = reader(csv_file)
            for row in csv_reader:
                Ingredient.objects.update_or_create(
                    name=row[0].strip(),
                    measurement_unit=row[1].strip()
                )
        self.stdout.write(self.style.SUCCESS('Список ингредиентов загружен!'))
