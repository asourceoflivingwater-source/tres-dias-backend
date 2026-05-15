from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from .services import DepartmentSectionsService
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from rest_framework.pagination import LimitOffsetPagination


class DepartmentsListView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]


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

    def get_queryset(self):
        department_id = self.kwargs.get("department_id")
        if not department_id:
            return DepartmentMember.objects.none()
        qs = DepartmentMember.objects.filter(department_id=department_id)
        user = self.request.user
        if not user.is_staff:
            is_chief_here = DepartmentMember.objects.filter(
                user=user,
                department_id=department_id,
                role="chief",
                is_active=True,
            ).exists()
            if not is_chief_here:
                return DepartmentMember.objects.none()
        return qs


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
