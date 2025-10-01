from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

from apps.core.models import BaseModel
from apps.department.models import Department, DepartmentRole 
from apps.sections.models import DepartmentSection 


User = get_user_model()

class AuditLog(BaseModel):
    actor = models.ForeignKey(User,on_delete=models.CASCADE, related_name='auditlogs')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='deaprtment_auditlogs')
    section = models.ForeignKey(DepartmentSection, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255, default="read_action")
    payload = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
    ]

class Comment(BaseModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_comments')
    author_role = models.CharField(max_length=20, choices=DepartmentRole.choices, default=DepartmentRole.ADMIN)
    label = models.CharField(max_length=100)
    body = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    is_admin_only = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]

class CommentAttachment(BaseModel):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to='comment_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'])]
    )
    filename = models.CharField(max_length=255)
    meta = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        super().save(*args, **kwargs)

