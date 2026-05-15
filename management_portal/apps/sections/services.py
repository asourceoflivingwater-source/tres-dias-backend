from .models import VersionedSection, SectionPermission
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .models import SectionStatus
from django.utils import timezone
from apps.adminapp.models import AuditLog


class VersionedSectionService:
    @staticmethod
    def get_version_sections(section_id):
        return VersionedSection.objects.filter(section_id=section_id)

    @staticmethod
    def revert_section_version(request, section_id, version):
        versioned_section = get_object_or_404(
            VersionedSection, section_id=section_id, version=version
        )
        section = versioned_section.section

        section.content_published = versioned_section.content
        section.status = SectionStatus.PUBLISHED
        section.published_by = request.user
        section.published_at = timezone.now()
        section.save()

        AuditLog.objects.create(
            actor=request.user,
            department=section.department,
            section=section,
            action="revert_version",
            payload={
                "section_id": str(section.id),
                "reverted_to_version": version,
                "reverted_by": str(request.user.id),
            },
        )

        return section


class SectionService:
    @staticmethod
    def publish_section(request, serializer):
        section = serializer.instance
        serializer.save(
            updated_by=request.user,
            published_by=request.user,
            status=SectionStatus.PUBLISHED,
            content_published=serializer.validated_data.get(
                "content_draft", section.content_draft
            )
            or {},
            content_draft={},
            published_at=timezone.now(),
        )
        last_version = section.versions.aggregate(Max("version"))["version__max"] or 0
        new_version = last_version + 1

        VersionedSection.objects.create(
            section=section,
            version=new_version,
            content=section.content_published,
            published_by=request.user,
        )

        AuditLog.objects.create(
            actor=request.user,
            department=section.department,
            section=section,
            action="publish_section",
            payload={
                "section_id": str(section.id),
                "version": new_version,
            },
        )


class SectionPermissionService:
    @staticmethod
    def get_section_permission(section_id, role):
        return get_object_or_404(
            SectionPermission,
            section_id=section_id,
            role=role,
        )
