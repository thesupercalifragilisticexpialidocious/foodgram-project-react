import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

DATA_DIR = './static/data/'  # '../data/'


def ord_str(s):
    result = 0
    for letter in s:
        result = result + ord(letter)
    return result


def parse_ingredients(path):
    """Parse name,unit rows."""
    ingredients = []
    mapping = {}
    for (code, unit) in Ingredient.UNIT_CHOICES:
        mapping[ord_str(unit)] = code
    with open(path, encoding='utf8') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ingredients.append(Ingredient(
                name=row[0],
                unit=mapping[ord_str(row[1])]
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
