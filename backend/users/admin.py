from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
