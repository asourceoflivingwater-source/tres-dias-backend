from .models import DepartmentMember
from ..sections.models import DepartmentSection, SectionPermission
from django.db.models import Q


class DepartmentSectionsService:
    @staticmethod
    def get_public_sections(slug):
        return DepartmentSection.objects.filter(
            department__slug=slug, status="published", visibility="public"
        )

    @staticmethod
    def get_role_sections(slug, user_id):

        member = DepartmentMember.objects.filter(
            user_id=user_id, department__slug=slug
        ).first()

        criteria = Q(visibility="public")

        if member:
            criteria |= Q(visibility="members")
            viewable_section_ids = SectionPermission.objects.filter(
                role=member.role,
                can_view=True,
                section__department__slug=slug,
            ).values_list("section_id", flat=True)
            criteria |= Q(
                visibility="role_scoped", id__in=viewable_section_ids
            )

        return DepartmentSection.objects.filter(
            department__slug=slug,
        ).filter(criteria)

    @staticmethod
    def get_all_sections(slug):
        return DepartmentSection.objects.filter(department__slug=slug)
