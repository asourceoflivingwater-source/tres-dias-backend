from rest_framework import status
from rest_framework.generics import ListCreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from apps.users.models import User
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from django.shortcuts import get_object_or_404
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
    def get_queryset(self):
        # Override get_queryset for the LIST part of ListCreateAPIView
        department_id = self.kwargs.get("department_id")
        return DepartmentMember.objects.filter(department_id=department_id)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.get(email=data["user_email"])
        data['user'] = user.id
        data['department'] = self.kwargs["department_id"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class DepartmentMemberUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsChief]
    serializer_class = DepartmentMemberSerializer
    queryset = DepartmentMember.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
       
        obj = get_object_or_404(queryset, department_id=self.kwargs.get('department_id'),
                                user_id=self.kwargs.get('user_id'))
        self.check_object_permissions(self.request, obj)
        return obj
    
class DepartmentSectionsView(ListAPIView):
    permission_classes = AllowAny    
    model = DepartmentSection
    serializer_class = DepartmentSectionSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        role = DepartmentMember.objects.get(user=user).role
        department_slug = self.kwargs.get('slug')
       
        mandatory_filters = {
            'department__slug': department_slug,
            'status': 'published',
        }
         
        if user.is_staff or role=="Chief":
            return DepartmentSection.objects.filter(*mandatory_filters)
        
        visibility_criteria = Q(visibility='public')
        
        if user.is_authenticated:
            # Add sections available for all memebers
            member_sections_q = Q(
                visibility='members',
                department__members__user=user,
            )
            # Add available role based sections         
            staff_sections_q = Q(visibility='role_based', visible_for_roles__contains=role)
            visibility_criteria |= staff_sections_q or member_sections_q

        queryset = DepartmentSection.objects.filter(
            **mandatory_filters
        ).filter(
            visibility_criteria
        ).order_by('order')

        return queryset
    
        
     


