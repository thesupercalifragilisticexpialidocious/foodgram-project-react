from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from recipes.models import Ingridient, Recipe, Tag
from users.models import Favorite, Follow, User


class ColorNormalizer(serializers.Field):
    """Conversion betwseen "#E26C2D"-format strings and int."""
    def to_representation(self, value):
        string = f'{value:X}'
        return f'#{"0"*(6-len(string))}{string}'
    def to_internal_value(self, data):
        return int(data[1:], 16)


class DurationNormalizer(serializers.Field):
    """Conversion between time intervals and int for minutes."""
    def to_representation(self, value):
        return round(value.total_seconds / 60)
    def to_internal_value(self, data):
        return timedelta(minutes=data)


class IngridientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='unit', read_only=True)
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    color = ColorNormalizer()
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializerSafe(serializers.ModelSerializer):
    name = serializers.CharField(source='title', read_only=True)
    text = serializers.CharField(source='description', read_only=True)
    cooking_time = DurationNormalizer()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingridients = IngridientPerRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'text',
            'tags',
            'author',
            'ingridients',
            'is_favorited',
            # 'is_in_shopping_cart',
            'image',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        return True or False


class RecipeSerializerSafe(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
