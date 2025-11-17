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
            try:
                member = DepartmentMember.objects.get(user=request.user.id)    
                return member.role == 'chief' 
            except DepartmentMember.DoesNotExist:
                return False
        return False

class CanEditSection(IsChief):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        # Only allow for update actions
        if request.method not in ("PATCH", "PUT"):
            return False

        section_id = view.kwargs.get("section_id")

        try:
            member = DepartmentMember.objects.get(user=request.user, is_active=True)
            section = DepartmentSection.objects.filter(id=section_id).first()
        except DepartmentMember.DoesNotExist:
            return False
        
        return member.role == "chief" or member.role in section.allow_edit_roles
    
class CanPublishSection(IsChief):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        section_id = view.kwargs.get("section_id") 

        try:
            member = DepartmentMember.objects.get(user=request.user, is_active=True)
            section = DepartmentSection.objects.filter(id=section_id).first()
        except DepartmentMember.DoesNotExist():
            return False
        
        return member.role in section.allow_publish_roles or member.role=="chief"

class CanViewSection(IsRectorateOrClergy):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        
        section_id = view.kwargs.get("section_id") 
        try:
            member = DepartmentMember.objects.get(user=request.user, is_active=True)
            section = DepartmentSection.objects.filter(id=section_id).first()
        except DepartmentMember.DoesNotExist:
            return False
        
        return member.role in section.visible_for_roles or member.role=='chief'
    