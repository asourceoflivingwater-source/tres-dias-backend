from rest_framework.permissions import BasePermission, IsAuthenticated
from apps.department.models import Department, DepartmentMember
from django.shortcuts import get_object_or_404
from apps.department.models import DepartmentRole
from apps.sections.models import SectionPermission
from logging import getLogger

logger = getLogger(__name__)

class IsDepartmentMember(IsAuthenticated):

    def has_permission(self, request, view):
        
        if not super().has_permission(request, view):
            return False
        
        department_slug = view.kwargs.get('slug')
        department_id = view.kwargs.get('id')
        if not department_slug and not department_id:
            return False
        try:
            
            if department:
                department = Department.objects.get(slug=department_slug)
            else:
                department = Department.objects.get(id=department_id)
            is_member = DepartmentMember.objects.filter(
            user=request.user,
            department=department,
            is_active=True
            ).exists()
            
            return is_member
            
        except Department.DoesNotExist:
            return False

class IsRectorate(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_rectorate
    
class IsClergy(BasePermission):

    def has_permission(self, request, view):

        return request.user.clergy

class IsChief(BasePermission):

    def has_permission(self, request, view):
        department_member = get_object_or_404(DepartmentMember, 
                                                user_id=request.user.id,
                                                )
        return department_member.role == DepartmentRole.CHIEF
    
class SectionEditPermission(BasePermission):
    
    def has_permission(self, request, view):
        section_id = view.kwargs.get("section_id") 

        department_member = get_object_or_404(
            DepartmentMember,
            user_id=request.user.id
        )

        role = department_member.role
        section_permission = get_object_or_404(
            SectionPermission,
            section_id=section_id,
            role=role
        )


        if request.method in ("GET", "HEAD", "OPTIONS"):
            return section_permission.can_view
        elif request.method in ("PUT", "PATCH"):
            return section_permission.can_edit
        elif request.method == "POST":
            return section_permission.can_publish
            
        