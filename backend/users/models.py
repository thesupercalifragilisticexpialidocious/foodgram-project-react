from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()


class Follow(models.Model):
    STR_PRESENTATION = '@{user} follows @{author}'
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed_by',
        verbose_name='автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow_relation'
            ),
        )

    def __str__(self):
        return self.STR_PRESENTATION.format(
            user=self.user.username,
            author=self.author.username,
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


"""
class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Administrator'),
    ]

    bio = models.CharField(max_length=250, null=True, blank=True)
    role = models.CharField(max_length=20, default='user', choices=ROLES)
    confirmation_code = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(unique=True)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ['id']
"""