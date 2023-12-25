from django.core.management.base import BaseCommand

from foodgram_api.import_data import create_tags


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_tags()
