from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
  
    readonly_fields = ('id',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('id', 'is_rectorate', 'is_clergy')}),
    )

admin.site.register(User, CustomUserAdmin)