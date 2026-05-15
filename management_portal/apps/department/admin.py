from django.contrib import admin
from .models import Department, DepartmentMember, DepartmentContact


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "id")
    search_fields = ("title", "slug")
    ordering = ("title",)


admin.site.register(DepartmentMember)
admin.site.register(DepartmentContact)
