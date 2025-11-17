from rest_framework.generics import ListCreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q

class DepartmentsListView(ListCreateAPIView):
    permission_classes=[AllowAny]
    queryset = Department.objects.all()
    serializer_class= DepartmentSerializer

class DepartmentProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field='slug'
    lookup_url_kwarg='slug'

class DepartmentMemberView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsChief]
    model = DepartmentMember
    serializer_class= DepartmentMemberSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['department_id'] = self.kwargs.get("department_id")
        return context
    
class DepartmentMemberUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsChief]
    serializer_class = DepartmentMemberSerializer
    queryset = DepartmentMember.objects.all()
    lookup_field = 'user'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        return DepartmentMember.objects.filter(department_id=department_id)

class DepartmentSectionsView(ListAPIView):
    permission_classes = [AllowAny]    
    model = DepartmentSection
    serializer_class = DepartmentSectionSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        role = None
        if user.is_authenticated and not user.is_staff :
            role = DepartmentMember.objects.get(user=user).role
        department_slug = self.kwargs.get('slug')
       
        mandatory_filters = {
            'department__slug': department_slug,
            'status': 'published',
        }
         
        if user.is_authenticated and (user.is_staff or role=="Chief"):
            return DepartmentSection.objects.filter(**mandatory_filters)
        
        visibility_criteria = Q(visibility='public')
        
        if user.is_authenticated:
            # Add sections available for all memebers
            member_sections_q = Q(
                visibility='members',
                department__members__user=user,
            )
            # Add available role based sections         
            staff_sections_q = Q(visibility='role_based', visible_for_roles__icontains=role)
            visibility_criteria |= staff_sections_q or member_sections_q

        queryset = DepartmentSection.objects.filter(
            **mandatory_filters
        ).filter(
            visibility_criteria
        )

        return queryset
    
        
     


