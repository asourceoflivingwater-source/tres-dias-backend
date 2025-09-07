from django.db import models
from apps.department.models import Department, DepartmentRole
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()

class SectionType(models.TextChoices):

    HOME = 'HOME', 'Home'
    CHIEF_INFO = 'CHIEF_INFO', 'Chief Info'
    TEAM_INFO = 'TEAM_INFO', 'Team Info'
    ASSISTANT_INFO = 'ASSISTANT_INFO', 'Assistant Info'
    SECRETARY_INFO = 'SECRETARY_INFO', 'Secretary Info'
    INTERACTIONS = 'INTERACTIONS', 'Interactions'
    MEDIA = 'MEDIA', 'Media'

class SectionStatus(models.TextChoices):

    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'

class VisibilityType(models.TextChoices):

    PUBLIC = 'public', 'Public'
    MEMBERS = 'members', 'All Members'
    ROLE_SCOPED = 'role_scoped', 'Role Scoped'

class MediaAssetKind(models.TextChoices):
    
    PHOTO = 'photo', 'Photo'
    VIDEO = 'video', 'Video'


class DepartmentSection(BaseModel):

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sections')
    type = models.CharField(max_length=20, choices=SectionType.choices)
    title = models.CharField(max_length=255)
    content_draft = models.JSONField(default=dict, blank=True)
    content_published = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=10, choices=SectionStatus.choices, default=SectionStatus.DRAFT)
    visibility = models.CharField(max_length=15, choices=VisibilityType.choices, default=VisibilityType.PUBLIC)
    visible_for_roles = models.JSONField(default=list, blank=True) 
    allow_edit_roles = models.JSONField(default=list, blank=True)
    allow_publish_roles = models.JSONField(default=list, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_sections')
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='published_sections')
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['department', 'type'], name='unique_section_type_per_department')
        ]

class SectionPermission(BaseModel):
    section = models.ForeignKey(DepartmentSection, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=DepartmentRole.choices)
    can_view = models.BooleanField()
    can_edit = models.BooleanField()
    can_publish = models.BooleanField()

class MediaAsset(BaseModel):

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='media_assets')
    section = models.ForeignKey(DepartmentSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='media_assets')
    file = models.FileField(
        upload_to='media_assets/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'])]
    )
    kind = models.CharField(max_length=10, choices=MediaAssetKind.choices)
    caption = models.CharField(max_length=255, blank=True)
    meta = models.JSONField(default=dict, blank=True)

class AuditLog(BaseModel):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='audit_logs')
    section = models.ForeignKey(DepartmentSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
        ]

class VersionedSection(BaseModel):
    section = models.ForeignKey(DepartmentSection, on_delete=models.CASCADE, related_name='versions')
    version = models.PositiveIntegerField()
    content = models.JSONField(default=dict)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='versioned_sections')
    published_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['section', 'version'], name='unique_section_version')
        ]
        ordering = ['section', '-version']