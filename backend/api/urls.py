from django.urls import include, path
from rest_framework import routers
from api.views import (FavorViewSet, IngridientViewSet, RecipeViewSet,
                       ShoppingListViewSet, SubscribeViewSet,
                       SubscriptionViewSet, TagViewSet,
                       TokenViewSet, UserViewSet, shopping_pdf)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngridientViewSet, basename='ingridients')
router.register(r'users', UserViewSet, basename='users')
# me?
router.register(
    r'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions'
)
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavorListViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingListViewSet,
    basename='shopping_cart'
)
router.register(r'auth/token', TokenViewSet)

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        shopping_pdf,
        name='shopping_pdf'
    ),
    path('', include(router.urls)),
]
