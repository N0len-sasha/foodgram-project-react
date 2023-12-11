from django.core.management.base import BaseCommand

from foodgram_api.import_data import (import_ingredients_from_csv,
                                      import_ingredients_from_json)


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_ingredients_from_json()
