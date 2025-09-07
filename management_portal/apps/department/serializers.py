from rest_framework import serializers
from .models import Department, DepartmentMember

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["title","slug","description","chief"]

class DepartmentMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMember
        fields = ['id', 'user_id', 'department_id', 'role']
        