from rest_framework import serializers
from .models import Department, DepartmentSection, DepartmentMember

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["title","slug","description","chief"]

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSection
        fields = ["department","type","title"]

class DepartmentMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMember
        fields = ['id', 'user_id', 'department_id', 'role']
        