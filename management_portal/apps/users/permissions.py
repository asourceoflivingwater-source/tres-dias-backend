from rest_framework.permissions import BasePermission, IsAuthenticated
from apps.department.models import Department, DepartmentMember
from apps.sections.models import DepartmentSection
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
    
class IsChief(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if not request.user.is_authenticated:
            return False
        return obj.members.filter(user=request.user, role='chief', is_active=True).exists()

class CanEditSection(BasePermission):
    def has_permission(self, request, view):

        
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True
        
        

        if not request.user.is_authenticated:
            return False
        section_id = view.kwargs.get("section_id") 
        member = DepartmentMember.objects.filter(user=request.user, is_active=True).first()
        section = DepartmentSection.objects.filter(id=section_id).first()
        if not member:
            return False
        
        role = member.role
        if request.method in ['PATCH', 'PUT']:
            return role in section.allow_edit_roles or member.role =='chief'

        return False
    
class CanPublishSection(BasePermission):
    def has_permission(self, request, view):

        
        if not request.user.is_authenticated:
            return False
        
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
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

class CanViewSection(BasePermission):
    def has_permission(self, request, view):

        
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
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
    
class IsChiefOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True
        member = DepartmentMember.objects.filter(user=request.user, is_active=True).first()
        return member.role == 'chief'