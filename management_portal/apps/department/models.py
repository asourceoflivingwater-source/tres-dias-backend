from django.contrib.auth import get_user_model
from django.db import models
from apps.core.models import BaseModel
from django.core.validators import FileExtensionValidator

User = get_user_model()

class DepartmentRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    CHIEF = 'chief', 'Chief'
    ASSISTANT = 'assistant', 'Assistant'
    SECRETARY = 'secretary', 'Secretary'
    TEAM_MEMBER = 'team_member', 'Team Member'
    VIEWER = 'viewer', 'Viewer'

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

class DepartmentContact(BaseModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='contacts')
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['full_name']