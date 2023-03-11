from datetime import date
from io import BytesIO
import logging

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import FlexiblePagination
from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (ChangePasswordSerializer, IngredientSerializer,
                             RecipeSerializerSafe, RecipeSerializerShort,
                             RecipeSerializerUnsafe, TagSerializer,
                             UserSerializer, UserFollowedSerializer)
from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import Follow, User
from shopping.models import ShoppingList


HORIZONTAL_OFFSET = 1
VERTICAL_OFFSET = 11
DOT_OFFSET = 100
HEADER_FONT_SIZE = 18
BODY_FONT_SIZE = 12


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = FlexiblePagination
    permission_classes = (IsAdminOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializerSafe
        if self.action in ('destroy', 'create', 'update', 'partial_update'):
            return RecipeSerializerUnsafe
        return RecipeSerializerShort

    def get_queryset(self):
        queryset = Recipe.objects.all()
        params = self.request.query_params
        logging.debug(params)

        tags = params.get('tags')
        logging.debug(tags)
        if tags is not None:
            queryset = queryset.filter(tags__slug__in=tags)
        logging.debug(queryset)
        author = params.get('author')
        if author is not None:
            queryset = queryset.filter(author=author)

        if params.get('is_favorited'):
            queryset = queryset.filter(
                is_favorited__in=Favorite.objects.filter(
                    user=self.request.user
                )
            )

        if params.get('is_in_shopping_cart'):
            queryset = queryset.filter(
                is_in_shopping_cart=ShoppingList.objects.get(
                    owner=self.request.user
                )
            )
        return queryset

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            Favorite.objects.create(
                user=request.user,
                recipe=recipe,
            )
            return Response(self.get_serializer(recipe).data)
        favorite = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            ShoppingList.objects.get_or_create(
                owner=request.user
            )[0].recipes.add(recipe)
            return Response(self.get_serializer(recipe).data)
        request.user.shopping_list.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        SHOPPING_STRING = '{name}{offset}{amount} {unit}'
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        text = pdf.beginText()
        text.setTextOrigin(HORIZONTAL_OFFSET * inch, VERTICAL_OFFSET * inch)
        text.setFont('Helvetica', HEADER_FONT_SIZE)
        text.textLine('FOODGRAM')
        pdfmetrics.registerFont(TTFont(
            'FreeSans',
            'api/static/fonts/FreeSans.ttf'
        ))
        text.setFont('FreeSans', BODY_FONT_SIZE)
        for pk, amount in (request.user.shopping_list
                           .calculate_ingredients().items()):
            ingredient = Ingredient.objects.get(pk=pk)
            text.textLine(SHOPPING_STRING.format(
                name=ingredient.name.capitalize(),
                offset='.' * (DOT_OFFSET - len(ingredient.name)),
                amount=amount,
                unit=ingredient.get_unit_display()
            ))
        pdf.drawText(text)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, filename=f'shopping_{date.today()}.pdf')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FlexiblePagination
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=('POST',),
        serializer_class=ChangePasswordSerializer
    )
    def set_password(self, request):
        user = self.request.user
        if not user.check_password(self.serializer.data.get(
            'current_password'
        )):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(self.serializer.data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=False,
        serializer_class=UserFollowedSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            is_subscribed__in=request.user.follows.all()
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        serializer_class=UserFollowedSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            Follow.objects.create(
                user=request.user,
                author=author,
            )
            return Response(self.get_serializer(author).data)
        follow = get_object_or_404(
            Follow,
            user=request.user,
            author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
