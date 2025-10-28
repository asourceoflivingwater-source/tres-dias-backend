from rest_framework.permissions import BasePermission, IsAuthenticated
from apps.department.models import Department, DepartmentMember
from apps.sections.models import DepartmentSection
from logging import getLogger
from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404


class IsStaffOrSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True
        
        return False
        
    
class IsChief(IsStaffOrSuperuser):
    def has_object_permission(self, request, view, obj):
        
        if not request.user.is_authenticated:
            return False
        return obj.members.filter(user=request.user, role='chief', is_active=True).exists()


class CanEditSection(BasePermission):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        user = request.user


        # Must be authenticated
        if not user.is_authenticated:
            return False

        # Only allow for update actions
        if request.method not in ("PATCH", "PUT"):
            return False

        section_id = view.kwargs.get("section_id")
        if not section_id:
            return False 
       
        member = (
            DepartmentMember.objects
            .select_related("department")
            .filter(user=user, is_active=True)
            .first()
        )
        if not member:
            return False

        section = get_object_or_404(DepartmentSection, id=section_id)
        
        return member.role == "chief" or member.role in section.allow_edit_roles

    
class CanPublishSection(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        section_id = view.kwargs.get("section_id") 

        if getattr(request.user, "is_staff", False):
            return True

        member = DepartmentMember.objects.filter(user=request.user, is_active=True).first()
        section = DepartmentSection.objects.filter(id=section_id).first()
        if not member:
            return False

        role = member.role
        if role == "chief":
            return True

        return role in section.allow_publish_roles

class CanViewSection(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        if getattr(request.user, "is_rectorate", False) or getattr(request.user, "is_clergy", False):
            return True
        
        section_id = view.kwargs.get("section_id") 
        member = DepartmentMember.objects.filter(user=request.user, is_active=True).first()
        section = DepartmentSection.objects.filter(id=section_id).first()
        if not member:
            return False

        if member.role == "chief":
            return True

        return member.role in section.visible_for_roles
    
class IsChiefOrAdmin(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        member = DepartmentMember.objects.filter(user=request.user, is_active=True).first()
        return member.role == 'chief'