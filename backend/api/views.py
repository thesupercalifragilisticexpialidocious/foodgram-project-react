from datetime import date
from io import BytesIO

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (ChangePasswordSerializer, IngridientSerializer,
                             RecipeSerializerSafe,
                             RecipeSerializerShort, RecipeSerializerUnsafe,
                             TagSerializer, TokenSerializer,
                             UserSerializer, UserFollowedSerializer)
from recipes.models import Ingridient, Recipe, Tag
from users.models import Favorite, Follow, User


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_favorited', 'is_in_shopping_cart',
                        'author', 'tags')
    permission_classes = (IsAdminOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializerSafe
        if self.action in ('destroy', 'create', 'update', 'partial_update'):
            return RecipeSerializerUnsafe
        return RecipeSerializerShort

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
            request.user.shopping_list.recipes.add(recipe)
            return Response(self.get_serializer(recipe).data)
        request.user.shopping_list.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(request):
        SHOPPING_STRING = '{name}{"."*(32-len(name))}{amount} {unit}'
        buffer = BytesIO()
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=False,
        serializer_class=UserFollowedSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        return Response(
            self.get_serializer(User.objects.filter(
                author__is_subscribed__in=request.user.follows,
                many=True
            ).data)
        )

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


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    serializer = TokenViewSet(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        email=serializer.validated_data['email']
    )
    user
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMDb registration',
        message=f'Your confirmation code: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)

class TokenViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
 viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = TokenSerializer

    def create(self, request, **kwargs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
