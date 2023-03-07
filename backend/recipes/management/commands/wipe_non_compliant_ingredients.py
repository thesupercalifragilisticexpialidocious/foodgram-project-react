from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Cleanses old ingridients from database.'

    def handle(self, *args, **options):
        c = Ingredient.objects.all().exclude(
            unit__in=[u[0] for u in Ingredient.UNIT_CHOICES]
        ).delete()
        self.stdout.write(self.style.SUCCESS(f'{c} ingredients were removed'))
