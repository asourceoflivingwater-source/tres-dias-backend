from django.contrib import admin
from .models import (
    Department, DepartmentMember, 
    DepartmentContact
)

admin.site.register(Department)
admin.site.register(DepartmentMember)
admin.site.register(DepartmentContact)
