from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import DepartmentSection, VersionedSection, MediaAsset, SectionPermission

class DepartmentSectionSerializer(ModelSerializer):
    class Meta:
        model = DepartmentSection
        fields = ["department","type", "title", 
                  "content_draft", "content_published", "visibility", "visible_for_roles", 
                  "allow_edit_roles", "allow_publish_roles", "status"]
        
class VersionSectionSerializer(ModelSerializer):
    class Meta:
        model = VersionedSection
        fields = ['id', 'section', 'version', 'content', 'created_at']
        
class SectionPermissionSerializer(ModelSerializer):
    class Meta:
        model = SectionPermission
        fields = ['id', 'section', 'role', 'can_view', 'can_edit', 'can_publish']

class MediaAssetSerializer(ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ['id', 'department', 'section', 'file', 'kind', 'caption', 'meta', 'created_at']

    def validate(self, data):
        if not data.get('kind'):
            ext = data['file'].name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                data['kind'] = 'image'
            elif ext in ['mp4', 'mov', 'avi']:
                data['kind'] = 'video'
            else:
                raise serializers.ValidationError("Unsupported file type.")
        return data
