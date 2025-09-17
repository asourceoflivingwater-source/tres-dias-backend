from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db.models import Max

from .models import DepartmentSection, SectionStatus, VersionedSection, SectionPermission
from .serializers import (DepartmentSectionSerializer, 
                          MediaAssetSerializer, 
                          SectionPermissionSerializer,
                          VersionSectionSerializer)

from apps.users.permissions import CanEditSection, CanPublishSection, IsChiefOrAdmin




class SectionsView(APIView):

    permission_classes = [CanEditSection]
    
    def post(self, request, section_id):
        self.section_id = section_id
        serializer = DepartmentSectionSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Section created successfully",
                "section": serializer.data
            }, status=status.HTTP_201_CREATED)

    def patch(self, request, section_id):
        self.section_id = section_id
        section = get_object_or_404(DepartmentSection, id=section_id)
        serializer = DepartmentSectionSerializer(
            instance=section,
            data = request.data,
            partial=True
        )
        if serializer.is_valid():
           
            serializer.save(updated_by=request.user)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SectionsPublishView(APIView):

    permission_classes = [CanPublishSection]

    def post(self, request, section_id):

        section = get_object_or_404(DepartmentSection, id=section_id)
        serializer = DepartmentSectionSerializer(
            instance=section,
            data = request.data,
            partial=True
        )
        if serializer.is_valid():
           
            serializer.save(updated_by=request.user,
                            published_by=request.user,
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
                content= serializer.validated_data.get("content_published", section.content_published) or {},
                published_by=request.user,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SectionPermissionEditView(APIView):
    permission_classes = [IsChiefOrAdmin]

    def patch(self, request, section_id):
        
        permission = get_object_or_404(SectionPermission, section_id=section_id)
        serializer = SectionPermissionSerializer(
            instance=permission,
            data = request.data,
            partial=True
        )
        if serializer.is_valid():
            permisison = serializer.save()
            return Response(SectionPermissionSerializer(permisison).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SectionVersionsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, section_id):
        section_versions = VersionedSection.objects.filter(section_id=section_id)
        serializer = VersionSectionSerializer(section_versions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
    
class MediaUploadView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):

        serializer = MediaAssetSerializer(data=request.data)

        if serializer.is_valid():
            department = serializer.validated_data['department']
            media_asset = serializer.save(department=department)

            return Response(MediaAssetSerializer(media_asset).data, status = status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


        







