from django.contrib.auth import get_user_model
from django.db import models
from apps.core.models import BaseModel, AuditModel
from django.core.validators import FileExtensionValidator

User = get_user_model()

class DepartmentRole(models.TextChoices):

    ADMIN = 'admin', 'Admin'
    CHIEF = 'chief', 'Chief'
    ASSISTANT = 'assistant', 'Assistant'
    SECRETARY = 'secretary', 'Secretary'
    TEAM_MEMBER = 'team_member', 'Team Member'
    VIEWER = 'viewer', 'Viewer'
    RECTORATE = 'rectorate', 'Rectorate'
    CLERGY = 'clergy', 'Clergy'

class Department(BaseModel):

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    chief = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')

class DepartmentMember(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='department_memberships')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=DepartmentRole.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'department'], name='unique_department_membership')
        ]


class DepartmentComment(AuditModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_comments')
    author_role = models.CharField(max_length=20, choices=DepartmentRole.choices, default=DepartmentRole.CHIEF)
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


class DepartmentCommentAttachment(BaseModel):
    comment = models.ForeignKey(DepartmentComment, on_delete=models.CASCADE, related_name='attachments')
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

class DepartmentContact(BaseModel):

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='contacts')
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['full_name']