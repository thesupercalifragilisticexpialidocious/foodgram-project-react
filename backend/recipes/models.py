from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


UNIT_CHOICES = (
    ('G', 'г'),
    ('KG', 'кг'),
    ('ML', 'мл'),
    ('TSP', 'ч. л.'),
    ('TBSP', 'ст. л.'),
    ('PC', 'шт.'),
    ('AD_LIB', 'по вкусу'),
    ('GLASS', 'стакан'),
    ('DROP', 'капля'),
    ('HANDFUL', 'горсть'),
    ('SLICE', 'кусок'),
    ('PACK', 'пакет'),
    ('BUNCH', 'пучок'),
    ('PINCH', 'щепотка'),
    ('CAN', 'банка'),
    ('PACKAGE', 'упаковка'),
)


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=32,
        verbose_name='название'
    )
    color = models.PositiveIntegerField(
        unique=True,
        validators=[
            MaxValueValidator(
                int('FFFFFF', 16),
                message='Максимльное значение - FFFFFF'
            )
        ]
    )
    slug = models.SlugField(
        unique=True,
        max_length=16,
        verbose_name='слаг'
    )

    class Meta:
        default_related_name = 'tag'
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='название'
    )
    unit = models.CharField(
        choices=UNIT_CHOICES,
        max_length=16,
        verbose_name='ед. измерения'
    )

    class Meta:
        default_related_name = 'ingredient'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'unit'),
                name='unique_ingredient_name_unit_relation'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    STR_PRESENTATION = ('{title} by {author} ({pub_date:.%Y.%m.%d})')
    title = models.CharField(
        max_length=64,
        verbose_name='название',
    )
    description = models.TextField(
        max_length=4096,
        unique=True,
        verbose_name='описание',
    )
    cooking_time = models.DurationField(verbose_name='время приготовления')
    image = models.ImageField(
        upload_to='recipes/',
        unique=True,
        verbose_name='фото',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата и время опубликования',
    )
    author = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')

    class Meta:
        default_related_name = 'recipe'
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.STR_PRESENTATION.format(
            title=self.title,
            author=self.author.username,
            pub_date=self.pub_date,
        )


class IngredientPerRecipe(models.Model):
    STR_PRESENTATION = '{recipe} requires {amount} {unit} of {foodstuff}'
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='used_in',
    )
    amount = models.FloatField(
        validators=[
            MinValueValidator(0.01, message='Укажите число не менее 0.01'),
            MaxValueValidator(8192, message='Укажите число до 8000')
        ],
        verbose_name='количество'
    )

    class Meta:
        verbose_name = 'ингридиент на блюдо'
        verbose_name_plural = 'ингридиенты на блюда'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_dish_relation'
            ),
        )

    def __str__(self):
        return self.STR_PRESENTATION.format(
            recipe=self.recipe.title,
            amount=self.amount,
            unit=self.ingredient.unit,
            foodstuff=self.ingredient.name
        )


class Favorite(models.Model):
    STR_PRESENTATION = '{user} favors {recipe}'
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favors',
        verbose_name='добавил в избранное',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited',
        verbose_name='избранный рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_relation'
            ),
        )

    def __str__(self):
        return self.STR_PRESENTATION.format(
            user=self.user.username,
            recipe=self.recipe.title,
        )
