from rest_framework.permissions import BasePermission, IsAuthenticated
from apps.department.models import Department, DepartmentMember
from apps.sections.models import DepartmentSection, SectionPermission


class IsStaffOrSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True
        
        return False
        
class IsRectorateOrClergy(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        if getattr(request.user, "is_rectorate", False) or getattr(request.user, "is_clergy", False):
            return True
        
        return False
        
class IsChief(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        if request.user.is_authenticated:
            department_id = (
                view.kwargs.get("department_id")
                or view.kwargs.get("id")
                or getattr(view, "department_id", None)
            )
            qs = DepartmentMember.objects.filter(
                user=request.user,
                role="chief",
                is_active=True,
            )
            if department_id:
                qs = qs.filter(department_id=department_id)
            return qs.exists()
        return False

class CanEditSection(IsChief):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        section_id = view.kwargs.get("section_id") or view.kwargs.get("id")
        if not section_id:
            return False
        try:
            section = DepartmentSection.objects.select_related("department").get(pk=section_id)
        except DepartmentSection.DoesNotExist:
            return False
        member = DepartmentMember.objects.filter(
            user=request.user,
            department=section.department,
            is_active=True,
        ).first()
        if not member:
            return False
        perm = SectionPermission.objects.filter(
            section=section, role=member.role
        ).first()
        return bool(perm and perm.can_edit)
    
class CanPublishSection(IsChief):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        section_id = view.kwargs.get("section_id") or view.kwargs.get("id")
        if not section_id:
            return False
        try:
            section = DepartmentSection.objects.select_related("department").get(pk=section_id)
        except DepartmentSection.DoesNotExist:
            return False
        member = DepartmentMember.objects.filter(
            user=request.user,
            department=section.department,
            is_active=True,
        ).first()
        if not member:
            return False
        perm = SectionPermission.objects.filter(
            section=section, role=member.role
        ).first()
        return bool(perm and perm.can_publish)

class CanViewSection(IsRectorateOrClergy):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        section_id = view.kwargs.get("section_id") or view.kwargs.get("id")
        if not section_id:
            return False
        try:
            section = DepartmentSection.objects.select_related("department").get(pk=section_id)
        except DepartmentSection.DoesNotExist:
            return False
        member = DepartmentMember.objects.filter(
            user=request.user,
            department=section.department,
            is_active=True,
        ).first()
        if not member:
            return False
        perm = SectionPermission.objects.filter(
            section=section, role=member.role
        ).first()
        return bool(perm and perm.can_view)
    