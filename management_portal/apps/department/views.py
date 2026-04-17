from rest_framework.generics import (
    ListCreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from .services import DepartmentSectionsService
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from rest_framework.pagination import LimitOffsetPagination


class DepartmentsListView(ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = LimitOffsetPagination


class DepartmentProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class DepartmentMemberView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsChief]
    model = DepartmentMember
    serializer_class = DepartmentMemberSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["department_id"] = self.kwargs.get("department_id")
        return context


class DepartmentMemberUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsChief]
    serializer_class = DepartmentMemberSerializer
    queryset = DepartmentMember.objects.all()
    lookup_field = "user"
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        department_id = self.kwargs.get("department_id")
        return DepartmentMember.objects.filter(department_id=department_id)


class DepartmentSectionView(ListAPIView):

    permission_classes = [AllowAny]
    model = DepartmentSection
    serializer_class = DepartmentSectionSerializer
    pagination_class = LimitOffsetPagination
    service = DepartmentSectionsService

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        user = self.request.user
        service = DepartmentSectionsService()

        if user.is_authenticated and (user.is_superuser or user.is_staff):
            return service.get_all_sections(slug)

        if user.is_authenticated:
            return service.get_role_sections(slug, user.id)

        return service.get_public_sections(slug)
