from django.contrib import admin
from .models import AdminDepartmentComment, AdminCommentAttachment, AuditLog

admin.site.register(AdminDepartmentComment)
admin.site.register(AdminCommentAttachment)
admin.site.register(AuditLog)