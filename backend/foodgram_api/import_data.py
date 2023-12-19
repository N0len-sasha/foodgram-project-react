import csv
import json
from django.db import transaction
from .models import Ingredient


def import_ingredients_from_csv():
    with open('data/ingredients.csv',
              'r',
              encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        with transaction.atomic():
            for row in csv_reader:
                name, measurement_unit = map(str.strip, row)
                Ingredient.objects.create(name=name,
                                          measurement_unit=measurement_unit)
    print('Данные из CSV загружены')


def import_ingredients_from_json():
    with open('C:/Dev/foodgram-project-react/data/ingredients.json',
              'rb') as f:
        data = json.load(f)

        for el in data:
            Ingredient.objects.create(name=el['name'],
                                      unit=el['measurement_unit'])
    print('Данные из JSON загружены')
