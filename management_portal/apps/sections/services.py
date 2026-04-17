from .models import VersionedSection, SectionPermission
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .models import SectionStatus
from datetime import datetime


class VersionedSectionService:
    def get_version_sections(section_id):
        return VersionedSection.objects.filter(section_id)

    def revert_section_version(request, section_id, version):
        versioned_section = get_object_or_404(
            VersionedSection, section_id=section_id, version=version
        )
        section = versioned_section.section

        section.content_published = versioned_section.content
        section.status = "published"
        section.published_by = request.user
        section.save()

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
            content_draft=[],
            published_at=datetime.now(),
        )
        last_version = section.versions.aggregate(Max("version"))["version__max"] or 0
        new_version = last_version + 1

        VersionedSection.objects.create(
            section=section,
            version=new_version,
            content=serializer.validated_data.get(
                "content_published", section.content_published
            )
            or {},
            published_by=request.user,
        )


class SectionPermissionService:
    @staticmethod
    def get_section_permission(section_id, role):

        obj = get_object_or_404(
            SectionPermission.objects.all(),
            section_id=section_id,
            role=role,
        )

        return obj
