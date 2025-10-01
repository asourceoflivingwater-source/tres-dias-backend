from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import (ListCreateAPIView, 
                                     RetrieveUpdateDestroyAPIView, 
                                     UpdateAPIView,
                                     ListAPIView)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Max

from .models import DepartmentSection, SectionStatus, VersionedSection, SectionPermission, MediaAsset
from .serializers import (DepartmentSectionSerializer, 
                          MediaAssetSerializer, 
                          SectionPermissionSerializer,
                          VersionSectionSerializer)

from apps.users.permissions import CanEditSection, CanPublishSection, IsChief



class SectionsView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSectionSerializer
    queryset = DepartmentSection.objects.all()
    
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

    def perform_update(self, serializer):
        section = serializer.instance
        serializer.save(updated_by=self.request.user,
                            published_by=self.request.user,
                            status=SectionStatus.PUBLISHED,
                            content_published=serializer.validated_data.get(
                                "content_draft", section.content_draft
                                ) or {},
                            content_draft=[]
                            )
        last_version = section.versions.aggregate(Max("version"))["version__max"] or 0
        new_version = last_version + 1

        VersionedSection.objects.create(
            section=section,
            version=new_version,
            content = serializer.validated_data.get("content_published", section.content_published) or {},
            published_by=self.request.user,
            )
     
class SectionPermissionEditView(UpdateAPIView):
    permission_classes = [IsAdminUser|IsChief]
    serializer_class = SectionPermissionSerializer
    queryset = SectionPermission.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
       
        obj = get_object_or_404(queryset, section_id=self.kwargs.get('section_id'),
                                role=self.request.data.get('role'))
        self.check_object_permissions(self.request, obj)
        return obj
    
class SectionVersionsView(ListAPIView):
    permission_classes = [IsAdminUser|IsChief]
    serializer_class = VersionSectionSerializer
    
    def get_queryset(self):
        return VersionedSection.objects.filter(section_id=self.kwargs.get("section_id"))
    
class SectionVersionRevertView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, section_id, version):
        versioned_section = get_object_or_404(VersionedSection, section_id=section_id, version=version)
        section = versioned_section.section

        section.content_published = versioned_section.content
        section.status = "published"
        section.published_by = request.user
        section.save()

        serializer = DepartmentSectionSerializer(section)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MediaUploadView(ListCreateAPIView):
    permission_classes = [IsAdminUser| IsChief]
    serializer_class = MediaAssetSerializer
    queryset = MediaAsset.objects.all()
    
    


        







