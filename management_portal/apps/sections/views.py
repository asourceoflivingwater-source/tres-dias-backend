from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    ListAPIView,
)
from rest_framework import status

from .models import (
    DepartmentSection,
    SectionPermission,
    MediaAsset,
)
from .serializers import (
    DepartmentSectionSerializer,
    MediaAssetSerializer,
    SectionPermissionSerializer,
    VersionSectionSerializer,
)

from apps.users.permissions import CanEditSection, CanPublishSection, IsChief
from rest_framework.pagination import LimitOffsetPagination
from .services import VersionedSectionService, SectionService, SectionPermissionService


class SectionsView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSectionSerializer
    queryset = DepartmentSection.objects.all()
    pagination_class = LimitOffsetPagination


class SectionDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [CanEditSection]
    serializer_class = DepartmentSectionSerializer
    queryset = DepartmentSection.objects.all()
    lookup_field = "id"


class SectionsPublishView(UpdateAPIView):
    permission_classes = [CanPublishSection]
    serializer_class = DepartmentSectionSerializer
    queryset = DepartmentSection.objects.all()
    lookup_field = "id"
    service = SectionService

    def perform_update(self, serializer):
        self.service.publish_section(self.request, serializer)


class SectionPermissionEditView(UpdateAPIView):
    permission_classes = [IsChief]
    serializer_class = SectionPermissionSerializer
    queryset = SectionPermission.objects.all()
    service = SectionPermissionService

    def get_object(self):
        role = self.request.data.get("role")
        section_id = self.kwargs.get("section_id")
        return self.service.get_section_permission(section_id, role)


class SectionVersionsView(ListAPIView):
    permission_classes = [IsChief]
    serializer_class = VersionSectionSerializer
    pagination_class = LimitOffsetPagination
    service = VersionedSectionService

    def get_queryset(self):
        return self.service.get_version_sections(self.kwargs.get("section_id"))


class SectionVersionRevertView(APIView):
    permission_classes = [IsAdminUser]
    service = VersionedSectionService

    def post(self, request, section_id, version):
        reverted_section = self.service.revert_section_version(
            request, section_id, version
        )
        serializer = DepartmentSectionSerializer(reverted_section)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MediaUploadView(ListCreateAPIView):
    permission_classes = [IsChief]
    serializer_class = MediaAssetSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        department_id = self.request.query_params.get("department_id")
        qs = MediaAsset.objects.all()
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs
