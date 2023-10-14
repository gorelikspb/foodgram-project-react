from django.contrib import admin

from .models import Cart, Favorite, Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Cart)
admin.site.register(Favorite)
