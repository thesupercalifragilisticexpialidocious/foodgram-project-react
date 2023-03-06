from django.contrib import admin

from .models import Recipe, Tag, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'favorited_count')
    search_fields = ('text',)
    list_filter = ('author', 'title', 'tags')

    def favorited_count(self, obj):
        return obj.is_favorited.all().count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
