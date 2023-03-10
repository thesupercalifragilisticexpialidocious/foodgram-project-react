from base64 import b64decode
from datetime import timedelta

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientPerRecipe,
                            Recipe, Tag)
from shopping.models import ShoppingList
from users.models import Follow, User


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
        return round(value.total_seconds() / 60)

    def to_internal_value(self, data):
        return timedelta(minutes=data)


class ImageDecoder(serializers.Field):
    """Base64 string decoding."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        format, imgstr = data.split(';base64,')
        return ContentFile(
            b64decode(imgstr),
            name=f'temp.{format.split("/")[-1]}'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'id', 'is_subscribed')
        read_only_fields = ('id', )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous and Follow.objects.filter(
            user=user,
            author=obj
        ).exists())


class TagSerializer(serializers.ModelSerializer):
    color = ColorNormalizer()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(
        source='get_unit_display',
        read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientPerRecipeSerializerSafe(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = IngredientPerRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_measurement_unit(self, obj):
        return obj.ingredient.get_unit_display()

    def get_name(self, obj):
        return obj.ingredient.name


class RecipeSerializerSafe(serializers.ModelSerializer):
    name = serializers.CharField(source='title', read_only=True)
    text = serializers.CharField(source='description', read_only=True)
    cooking_time = DurationNormalizer()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientPerRecipeSerializerSafe(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous and ShoppingList.objects.filter(
            owner=self.context['request'].user,
            recipes=obj
        ).exists())


class IngredientPerRecipeSerializerUnsafe(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientPerRecipe
        fields = ('id', 'amount')


class RecipeSerializerUnsafe(serializers.ModelSerializer):
    name = serializers.CharField(source='title')
    text = serializers.CharField(source='description')
    cooking_time = DurationNormalizer()
    image = ImageDecoder()
    ingredients = IngredientPerRecipeSerializerUnsafe(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'tags', 'author',
                  'ingredients', 'image', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        composition = []
        # spec's OrderedDict([('ingredient',<Ingredient:рис>),('amount',10.0)])
        for ingredient_specification in ingredients:
            composition.append(IngredientPerRecipe(
                recipe=recipe,
                **ingredient_specification
            ))
        IngredientPerRecipe.objects.bulk_create(composition)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.update(**validated_data)
        old_composition = set(recipe.ingredients)
        new_composition = set()
        for ingredient_specification in ingredients:
            new_composition.add(IngredientPerRecipe(
                recipe=recipe,
                **ingredient_specification
            ))
        new_ingredients = new_composition.difference(old_composition)
        outdated_ingredients = old_composition.difference(new_composition)
        outdated_ingredients.delete()
        IngredientPerRecipe.objects.bulk_create(new_ingredients)
        recipe.tags.remove()
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous and ShoppingList.objects.filter(
            owner=self.context['request'].user,
            recipes=obj
        ).exists())


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
        user = self.context['request'].user
        return (not user.is_anonymous and Follow.objects.filter(
            user=user,
            author=obj
        ).exists())

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'old_password')
