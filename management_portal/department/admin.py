from django.contrib import admin
from .models import (
    Department, DepartmentMember, DepartmentSection, MediaAsset,
    AuditLog, VersionedSection, DepartmentComment, 
    DepartmentCommentAttachment, DepartmentContact
)

admin.site.register(Department)
admin.site.register(DepartmentMember)
admin.site.register(DepartmentSection)
admin.site.register(MediaAsset)
admin.site.register(AuditLog)
admin.site.register(VersionedSection)
admin.site.register(DepartmentComment)
admin.site.register(DepartmentCommentAttachment)
admin.site.register(DepartmentContact)