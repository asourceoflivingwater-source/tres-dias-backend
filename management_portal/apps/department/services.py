from .models import DepartmentMember
from ..sections.models import DepartmentSection
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
            criteria |= Q(
                visibility="role_based", visible_for_roles__icontains=member.role
            )

        return DepartmentSection.objects.filter(
            department__slug=slug,
        ).filter(criteria)

    @staticmethod
    def get_all_sections(slug):
        return DepartmentSection.objects.filter(department__slug=slug)

    """
    def get_available_sections(request):
        user = request.user
        role = None

        if user.is_staff:
            return DepartmentSection.objects.all()

        if user.is_authenticated:
            role = DepartmentMember.objects.get(user=user).role

        department_slug = request.kwargs.get("slug")

        mandatory_filters = {
            "department__slug": department_slug,
            "status": "published",
        }

        visibility_criteria = Q(visibility="public")

        if user.is_authenticated:

            member_sections_q = Q(
                visibility="members",
                department__members__user=user,
            )

        if user.is_authenticated and role:
            staff_sections_q = Q(
                visibility="role_based", visible_for_roles__icontains=role
            )

            visibility_criteria |= staff_sections_q or member_sections_q

        queryset = DepartmentSection.objects.filter(**mandatory_filters).filter(
            visibility_criteria
        )
    """
