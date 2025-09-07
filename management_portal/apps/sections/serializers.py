from rest_framework.serializers import ModelSerializer

from .models import DepartmentSection

class DepartmentSectionSerializer(ModelSerializer):
    class Meta:
        model = DepartmentSection
        fields = ["department","type", "title", 
                  "content_draft", "content_published", "visibility", "visible_for_roles", 
                  "allow_edit_roles", "allow_publish_roles", "status"]