from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import DepartmentSection, SectionStatus, VersionedSection, SectionPermission
from .serializers import DepartmentSectionSerializer, MediaAssetSerializer, SectionPermissionSerializer
from rest_framework.permissions import IsAdminUser
from apps.users.permissions import IsChief
from django.db.models import Max
from rest_framework.parsers import MultiPartParser, FormParser



class SectionsEditView(APIView):

    permission_classes = [IsAdminUser| IsChief]

    def patch(self, request, section_id):

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

    permission_classes = [IsAdminUser| IsChief]

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
                content= serializer.validated_data.get("contenr_published", section.content_published) or {},
                published_by=request.user,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SectionPermissionEditView(APIView):
    permission_classes = []

    def patch(self, request, section_id):
        
        permission = get_object_or_404(SectionPermission, section_id=section_id)
        serializer = SectionPermissionSerializer(
            instance=permission,
            data = request.data,
            partial=True
        )
        if serializer.is_valid():
            permisison = serializer.save(updated_by=request.user,
                            status=SectionStatus.PUBLISHED,
                            )
            return Response(SectionPermissionSerializer(permisison).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MediaUploadView(APIView):
    permission_classes = []
    def post(self, request):

        serializer = MediaAssetSerializer(data=request.data)

        if serializer.is_valid():
            department = serializer.validated_data['department']
            user = request.user
            media_asset = serializer.save()

            return Response(MediaAssetSerializer(media_asset).data, status = status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        







