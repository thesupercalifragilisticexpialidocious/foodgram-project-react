from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """The answer is пекарский порошок & стейк семги."""
    help = 'Seeks duplicates among ingredients.'

    def handle(self, *args, **options):
        lst = list(Ingredient.objects.all())
        n = len(lst)
        for i in range(n):
            for j in range(i+1, n):
                if lst[i].name == lst[j].name:
                    self.stdout.write(
                        self.style.SUCCESS(lst[i].name)
                    )
