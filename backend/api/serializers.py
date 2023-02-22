from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from recipes.models import Ingridient, IngridientPerRecipe, Recipe, Tag
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


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    """username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'id', 'is_subscribed')
        read_only_fields = ('id', )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    color = ColorNormalizer()

    class Meta:
        model = Tag
        fields = '__all__'


class IngridientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='unit', read_only=True)

    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')


class IngridientPerRecipeSerializerSafe(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = IngridientPerRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_measurement_unit(self, obj):
        return obj.ingredient.unit

    def get_name(self, obj):
        return obj.ingredient.name


class RecipeSerializerSafe(serializers.ModelSerializer):
    name = serializers.CharField(source='title', read_only=True)
    text = serializers.CharField(source='description', read_only=True)
    cooking_time = DurationNormalizer()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingridients = IngridientPerRecipeSerializerSafe(many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
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
        return Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()


class IngridientPerRecipeSerializerUnsafe(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingridient',
        queryset=Ingridient.objects.all()
    )

    class Meta:
        model = IngridientPerRecipe
        fields = ('id', 'amount')


class RecipeSerializerUnsafe(serializers.ModelSerializer):
    name = serializers.CharField(source='title')
    text = serializers.CharField(source='description')
    cooking_time = DurationNormalizer()
    ingridients = IngridientPerRecipeSerializerUnsafe(many=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Tag
        fields = ('name', 'text', 'tags', 'author',
                  'ingridients', 'image', 'cooking_time')


class RecipeSerializerShort(serializers.ModelSerializer):
    """Used in subscriptions, favorites, and shopping list POST responses."""
    name = serializers.CharField(source='title', read_only=True)
    cooking_time = DurationNormalizer()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowedSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSerializerShort(many=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'id', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('username', 'email', 'first_name',
                            'last_name', 'id',
                            'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
