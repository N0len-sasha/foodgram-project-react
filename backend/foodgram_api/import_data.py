import csv
import json

from termcolor import colored

from .models import Ingredient, Tag


def import_ingredients_from_csv():
    try:
        with open('data/ingredients.csv',
                  'r',
                  encoding='utf-8') as csv_file:

            print(colored('Началась загрузка ингредиентов', 'yellow'))

            for name, measurement_unit in csv.reader(csv_file):
                Ingredient.objects.create(
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

    tags_data = [
        {'name': 'Завтрак', 'color': '#EE204D', 'slug': 'breakfast'},
        {'name': 'Обед', 'color': '#008000', 'slug': 'lunch'},
        {'name': 'Ужин', 'color': '#78DBE2', 'slug': 'dinner'},
    ]

    for tag_data in tags_data:
        Tag.objects.create(**tag_data)

    print(colored('Загрузка тегов завершена успешно!', 'green'))
