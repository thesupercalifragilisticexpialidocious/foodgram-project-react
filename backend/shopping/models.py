from django.db import models

from recipes.models import Recipe
from users.models import User


class ShoppingList(models.Model):
    STR_PRESENTATION = ('{owner} fancies {recipes_number} recipes')
    owner = models.OneToOneField(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='is_in_shopping_cart'
    )

    class Meta:
        default_related_name = 'shopping_list'
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return self.STR_PRESENTATION.format(
            owner=self.owner.username,
            recipes_number=self.recipes.count(),
        )

    def calculate_ingredients(self):
        """Get dict {<ingredient pk>:<total amount of that ingredient>}."""
        wishlist = {}
        for recipe in self.recipes.all():
            for ingredient_specification in recipe.ingredients.all():
                ingredient_pk = ingredient_specification.ingredient.pk
                if ingredient_pk in wishlist:
                    wishlist[ingredient_pk] = (wishlist[ingredient_pk] +
                                               ingredient_specification.amount)
                else:
                    wishlist[ingredient_pk] = ingredient_specification.amount
        return wishlist
