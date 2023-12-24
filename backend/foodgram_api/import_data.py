import csv
import json

from django.db import transaction
from termcolor import colored

from .models import Ingredient, Tag


def import_ingredients_from_csv():
    try:
        with open('data/ingredients.csv',
                  'r',
                  encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            print(colored('Началась загрузка ингредиентов', 'yellow'))

            with transaction.atomic():
                for row in csv_reader:
                    name, measurement_unit = map(str.strip, row)
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )

        print(colored('Данные из CSV загружены', 'green'))

    except FileNotFoundError:
        print(colored('Error: File not found.', 'red'))

    except Exception as e:
        print(colored(f'Error: {e}', 'red'))


def import_ingredients_from_json():
    try:
        with open('/data/ingredients.json',
                  'rb') as f:
            data = json.load(f)
            print(colored('Началась загрузка ингредиентов', 'yellow'))

            for el in data:
                Ingredient.objects.create(name=el['name'],
                                          unit=el['measurement_unit'])
        print(colored('Данные из JSON загружены', 'green'))
    except FileNotFoundError:
        print(colored('Error: File not found.', 'red'))

    except Exception as e:
        print(f'Error: {e}', 'red')


def create_tags():
    print(colored('Началась загрузка тегов', 'yellow'))
    Tag.objects.get_or_create(name='Завтрак',
                              color='#EE204D',
                              slug='breakfast')
    Tag.objects.get_or_create(name='Обед',
                              color='#008000',
                              slug='lunch')
    Tag.objects.get_or_create(name='Ужин',
                              color='#78DBE2',
                              slug='dinner')
    print(colored('Загрузка тегов заверешена успешно!', 'green'))
