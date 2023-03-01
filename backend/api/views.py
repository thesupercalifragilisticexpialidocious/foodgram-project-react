from datetime import date
import io

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (IngridientSerializer, RecipeSerializerSafe,
                             RecipeSerializerShort, RecipeSerializerUnsafe,
                             TagSerializer)
from recipes.models import Ingridient, Recipe, Tag
from shopping.models import ShoppingList
from users.models import Favorite, Follow, User


class IngridientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    # permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (IsAdminUserOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_favorited', 'is_in_shopping_cart',
                        'author', 'tags')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializerSafe
        return RecipeSerializerUnsafe


class FavorViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerShort


, ShoppingListViewSet, SubscriptionViewSet,
SubscribeViewSet   TokenViewSet, UserViewSet


    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)

    def perform_update(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)

    def perform_destroy(self, review):
        review.delete()
        review.title.update_rating()





@action(detail=True, methods=['GET'])
@permission_classes([IsAuthenticated])
def shopping_pdf(request):
    SHOPPING_STRING = '{name}{"."*(32-len(name))}{amount} {unit}'
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)   
    text = canvas.beginText()
    text.setTextOrigin(3, 2.5*inch)
    text.setFont('Helvetica', 18)
    text.textLine('FOODGRAM')
    text.setFont('Helvetica-Oblique', 12)
    for ingridient, amount in request.user.shopping_list \
        .calculate_ingridients().items():
        text.textLine(SHOPPING_STRING.format(
            name=ingridient.name,
            amount=amount,
            unit=ingridient.unit
        ))
    pdf.drawText(text)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return FileResponse(buffer, filename=f'shopping_{date.today()}.pdf')
