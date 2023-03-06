import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

DATA_DIR = '../data/'


def parse_ingredients(path):
    """Parse name,unit rows."""
    ingredients = []
    with open(path) as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ingredients.append(Ingredient(
                name=row[0],
                unit=row[1]
            ))
    Ingredient.objects.bulk_create(ingredients)
    return len(ingredients)


class Command(BaseCommand):
    help = 'Parses csv file (name,unit rows) to fill a base with ingridients.'

    def handle(self, *args, **options):
        parse_cases = [
            [parse_ingredients, 'ingredients'],
        ]
        errors = []
        for func, file in parse_cases:
            try:
                total = func(f'{DATA_DIR}{file}.csv')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully parsed {file} for {total} rows'
                    )
                )
            except Exception as error:
                errors.append((file, error))
            if errors:
                raise CommandError(f'Cannot parse {errors}')
