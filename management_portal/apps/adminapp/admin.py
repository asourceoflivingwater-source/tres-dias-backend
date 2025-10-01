from django.contrib import admin
from .models import Comment, CommentAttachment, AuditLog

admin.site.register(Comment)
admin.site.register(CommentAttachment)
admin.site.register(AuditLog)