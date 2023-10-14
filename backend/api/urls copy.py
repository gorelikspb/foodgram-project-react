# api/urls.py
from django.urls import path
from .views import TagListView, TagDetailView
from djoser.views import TokenCreateView, TokenDestroyView
from .views import  IngredientListView, IngredientDetailView, CustomUserListCreateView
from .views import RecipeListCreateView, RecipeDetailView


urlpatterns = [
    path('users/', CustomUserListCreateView.as_view(), name='user-list-create'),
    path('auth/token/login/', TokenCreateView.as_view(), name='token-create'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='token-destroy'),    
    
    # path('users/', UserListView.as_view(), name='user-list'),
    # path('users/', UserCreateView.as_view(), name='user-registration'),
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list'),  # Список и создание рецептов
    # path('recipes/', RecipeListView.as_view(), name='recipe-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:id>/', TagDetailView.as_view(), name='tag-detail'),
    path('ingredients/<int:id>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    path('ingredients/', IngredientListView.as_view(), name='ingredient-list'),

    
]
