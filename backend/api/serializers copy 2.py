# api/serializers.py
import base64
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150, validators=[RegexValidator(regex='^[\w.@+-]+$', message='Invalid username format. Use only letters, numbers, and @/./+/-/_ characters.')])
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, max_length=150)

    def validate(self, attrs):
        return super().validate(attrs)
    

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)





class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)  # Вложенный сериализатор
    # fields = ('ingredient', 'amount')

    # ingredient = IngredientSerializer()  # Вложенный сериализатор для ингредиента

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True,
    )
    # ingredients = RecipeIngredientSerializer(many=True)  # Вложенный сериализатор для ингредиентов
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 
                  'ingredients', 'tags', 'cooking_time')

    def create(self, validated_data):
        print ('d13342423', validated_data)
        ingredients_data = self.initial_data.pop('ingredients')

        tags_data = self.initial_data.pop('tags')
        print ('!!!!!!!!!!!!!', tags_data)
        # tags_data = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)


        # Создаем связанные ингредиенты внутри рецепта
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)

        # Устанавливаем теги для рецепта

        return recipe
