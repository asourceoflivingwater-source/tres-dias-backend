from rest_framework.permissions import BasePermission
from apps.department.models import Department, DepartmentMember

class IsDepartmentMember(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        department_slug = view.kwargs.get('slug')
        if not department_slug:
            return False
        try:
            
            department = Department.objects.get(slug=department_slug)
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
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_rectorate
    
class IsClergy(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.clergy

class IsChief(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        