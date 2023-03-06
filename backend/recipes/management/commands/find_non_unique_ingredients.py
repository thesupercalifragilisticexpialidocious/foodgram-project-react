from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """The answer is пекарский порошок & стейк семги."""
    help = 'Seeks duplicates among ingredients.'

    def handle(self, *args, **options):
        ingredient_list = list(Ingredient.objects.all())
        ingredient_total_number = len(ingredient_list)
        for i in range(ingredient_total_number):
            for j in range(i+1, ingredient_total_number):
                if ingredient_list[i].name == ingredient_list[j].name:
                    self.stdout.write(
                        self.style.SUCCESS(ingredient_list[i].name)
                    )
