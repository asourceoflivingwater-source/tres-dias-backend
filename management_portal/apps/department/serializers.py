from rest_framework import serializers
from .models import Department, DepartmentMember
from apps.users.models import User

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id","title","slug","description","chief"]
        read_only_fields = ["id",]        

class DepartmentMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True) 

    class Meta:
        model = DepartmentMember
        fields = ["id", "user", "role", "is_active", "department", "user_email"]
        read_only_fields = ["id",  'department', 'user']

    def create(self, validated_data):
        
        user_email = validated_data.pop('user_email')
        department_id = self.context['department_id']
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_email': 'User with this email does not exist.'})
        
        department_member = DepartmentMember.objects.create(
            user=user,
            department_id=department_id,
            **validated_data
        )
        return department_member


