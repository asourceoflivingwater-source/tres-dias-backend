from django_filters import rest_framework as filters
from .models import AdminDepartmentComment
from uuid import UUID

class DepartmentCommentFilter(filters.FilterSet):
    department = filters.CharFilter(method='filter_department')
    created_at__gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    def filter_department(self, queryset, name, value):
        # Try UUID match
        try:
            uuid = UUID(value, version=4)
            return queryset.filter(department__id=uuid)
        except ValueError:
            # Fall back to slug match
            return queryset.filter(department__slug=value)

    class Meta:
        model = AdminDepartmentComment
        fields = ['department', 'author', 'author_role', 'tags']
