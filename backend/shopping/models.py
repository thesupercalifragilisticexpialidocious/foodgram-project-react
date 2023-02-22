from django.db import models

from recipes.models import Recipe
from users.models import User

class ShoppingList(models.Model):
    STR_PRESENTATION = ('{owner} fancies{list})')
    owner = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_lists'
    )

    class Meta:
        default_related_name = 'shopping_list'
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return self.STR_PRESENTATION.format(
            owner=self.owner.username,
            list=self.recipes,
        )

    def calculate_ingridients(self):
        """Get dict {<ingredient_pk>: <total amount of that ingridient>}."""
        wishlist = {}
        for recipe in self.recipes:
            for ingridient_specification in recipe.ingridients:
                ingridient = ingridient_specification.ingridient
                if ingridient in wishlist:
                    wishlist[ingridient] = (wishlist[ingridient] +
                                            ingridient_specification.amount)
                else:
                    wishlist[ingridient] = ingridient_specification.amount
        return wishlist
