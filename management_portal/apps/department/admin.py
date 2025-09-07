from django.contrib import admin
from .models import (
    Department, DepartmentMember, 
    DepartmentComment, 
    DepartmentCommentAttachment, DepartmentContact
)

admin.site.register(Department)
admin.site.register(DepartmentMember)
admin.site.register(DepartmentComment)
admin.site.register(DepartmentCommentAttachment)
admin.site.register(DepartmentContact)
