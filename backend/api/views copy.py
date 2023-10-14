# api/views.py
from django.contrib.auth import get_user_model
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from recipes.models import Recipe, Tag, Ingredient
from .serializers import  IngredientSerializer, RecipeSerializer, TagSerializer #UserSerializer,
from rest_framework import generics, status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rest_framework.generics import ListCreateAPIView

from django.contrib.auth import get_user_model

from .pagination import CustomPageNumberPagination

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
User = get_user_model()

from .serializers import CustomUserCreateSerializer

from .pagination import CustomPageNumberPagination  # Импортируйте вашу кастомную пагинацию

class RecipeListCreateView(ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination 
    permission_classes = [IsAuthenticatedOrReadOnly]  # Разрешение на аутентификацию при создании

    def perform_create(self, serializer):
        print ('!de33!!!!!!!!!!!', serializer)
        # При создании рецепта, устанавливаем автора текущего пользователя, если он аутентифицирован
        if self.request.user.is_authenticated:
            print('sdfsdfsf',self.request.user)
            serializer.save(author=self.request.user)

class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
 


class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__startswith=name)
        return queryset
    
class IngredientDetailView(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    lookup_field = 'id'


class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    pagination_class = CustomPageNumberPagination  # Используйте вашу кастомную пагинацию

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# class CustomUserCreateView(generics.CreateAPIView):
#     serializer_class = CustomUserCreateSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)



class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagDetailView(RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


# User = get_user_model()

# class UserCreateView(APIView):
#     def post(self, request):
#         serializer = CustomUserCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserListView(ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class UserCreateView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegistrationSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)