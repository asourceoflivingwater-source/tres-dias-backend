import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DepartmentSection, SectionPermission

DEFAULT_PERMISSIONS = [
    # (role,          can_view, can_edit, can_publish)
    ("admin",         True,  True,  True),
    ("chief",         True,  True,  True),
    ("assistant",     True,  False, False),
    ("secretary",     True,  False, False),
    ("team_member",   True,  False, False),
    ("viewer",        True,  False, False),
]


@receiver(post_save, sender=DepartmentSection)
def initialize_section_permissions(sender, instance, created, **kwargs):
    if not created:
        return
    perms = [
        SectionPermission(
            id=uuid.uuid4(),
            section=instance,
            role=role,
            can_view=can_view,
            can_edit=can_edit,
            can_publish=can_publish,
        )
        for role, can_view, can_edit, can_publish in DEFAULT_PERMISSIONS
    ]
    SectionPermission.objects.bulk_create(perms, ignore_conflicts=True)
