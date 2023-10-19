from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Follow

User = get_user_model()

# User serializers


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

# Recipes serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(
            shoppingcart__user=user, id=obj.id).exists()

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент для рецепта'
            }, code=400)

        ingredient_list = []

        for ingredient_item in ingredients:
            ingredient_id = ingredient_item.get('id')
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент с id {ingredient_id} не найден'
                }, code=400)

            if ingredient in ingredient_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными'
                }, code=400)

            ingredient_list.append(ingredient)

        return ingredients

# TODO Написал def для валидации тэгов. Теги валидируются, но при корректном
# создании рецепта ошибка: TypeError: Direct assignment to the forward side of
# a many-to-many set is prohibited. Use tags.set() instead.
#  TypeError: Direct assignment
# Но я и так уже  использую tags.set()!
# Попробовал несколько подходов но ничего не помогло.
# Валится даже если validate_tags сделать пустым, как ниже (

    # def validate_tags(self, tags):
    #     if not tags:
    #         raise serializers.ValidationError({
    #             'tags': 'Нужно выбрать хотя бы один тег для рецепта'
    #         }, code=400)

    #     tag_list = []

    #     for tag_id in tags:
    #         try:
    #             tag = Tag.objects.get(id=tag_id)
    #         except Tag.DoesNotExist:
    #             raise serializers.ValidationError({
    #                 'tags': f'Тег с id {tag_id} не найден'
    #             }, code=400)

    #         if tag in tag_list:
    #             raise serializers.ValidationError({
    #                 'tags': 'Теги должны быть уникальными'
    #             }, code=400)

    #         tag_list.append(tag)

    #     return tags

    # def validate_tags(self, tags):
    #     return tags

    def validate(self, data):
        # tags = self.initial_data.get('tags')
        # data['tags'] = self.validate_tags(tags)

        ingredients = self.initial_data.get('ingredients')
        data['ingredients'] = self.validate_ingredients(ingredients)
        return data

    def create_ingredients(self, ingredients, recipe):
        ingredient_amounts = [
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


class LiteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return LiteSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
