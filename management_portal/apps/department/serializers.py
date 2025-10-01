from rest_framework import serializers
from .models import Department, DepartmentMember
from apps.users.models import User

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id","title","slug","description","chief"]
        read_only_fields = ["id", ]
        

class DepartmentMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMember
        fields = ["id", "user", "role", "is_active", "department"]
        read_only_fields = ["id", ]
