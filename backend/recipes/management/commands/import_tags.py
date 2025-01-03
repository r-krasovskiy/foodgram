"""Модуль для импорта готовой базы тэгов из CSV-файла с тегами."""

import os
from csv import reader

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Tag

class Command(BaseCommand):
    """
    Загрузка данных из CSV файла с тегами в базу данных.

    Загружает список тегов из CSV файла в базу данных.
    Каждая строка CSV файла содержит название
    тега и его slug. Если тег уже существует в базе данных, его данные
    обновляются, в противном случае создается новый тег.
    """

    help = 'Загрузка списка тегов из csv-файла в базу данных.'

    def handle(self, *args, **options):
        """
        Чтение данных из CSV файла и их загрузка в базу данных.

        Читает файл tags.csv, обрабатывает каждую строку и загружает
        теги в модель Tag. Используется метод update_or_create, чтобы избежать
        дублирования записей.
        """
        file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'tags.csv')

        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = reader(csv_file)
            for row in csv_reader:
                Tag.objects.update_or_create(
                    name=row[0].strip(),
                    slug=row[1].strip()
                )
        self.stdout.write(self.style.SUCCESS('Список тегов загружен!'))
