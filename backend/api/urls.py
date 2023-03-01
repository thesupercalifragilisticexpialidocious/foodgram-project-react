from django.urls import include, path
from rest_framework import routers
from api.views import (IngridientViewSet, RecipeViewSet,
                       TagViewSet, TokenViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngridientViewSet, basename='ingridients')
router.register(r'users', UserViewSet, basename='users')
router.register(r'auth/token', TokenViewSet, basename='tokens')

urlpatterns = [path('', include(router.urls)),]
