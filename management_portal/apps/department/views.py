from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Department, DepartmentSection, DepartmentMember
from .serializers import DepartmentSerializer, SectionSerializer, DepartmentMemberSerializer
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from apps.users.models import User
from apps.users.permissions import IsDepartmentMember, IsChief

class DepartmentsListView(APIView):

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DepartmentProfileView(APIView):

    def get(self, request, slug):
        try:
            department = get_object_or_404(Department, slug=slug)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Department.DoesNotExist:
                return Response(
                    {"error": "Department not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

class DepartmentSectionsView(APIView):
    
    def get_permissions(self):
    
        if self.request.user.is_authenticated:
            return [IsAdminUser() or IsDepartmentMember()]
        else:
            return [AllowAny()]
    
    def get(self, request, slug):
        if request.user.is_authenticated:
            sections = DepartmentSection.objects.filter(department__slug=slug)
            serializer = SectionSerializer(sections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            sections = DepartmentSection.objects.filter(
                department__slug=slug,
                visibility='public',
                status='published'
            )
            serializer = SectionSerializer(sections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
     
class DepartmentAddMemberView(APIView):
    permission_classes = [IsAdminUser | IsChief]
    def post(self, request, department_id):
        user_email= request.data.get("user_email")
        role = request.data.get("role")
        department = Department.objects.get(id=department_id)
        user = User.objects.get(email=user_email)
        
        try:
            department_member = DepartmentMember.objects.create(
            department=department,
            user=user,
            role=role, 
            )
        except IntegrityError:
                return Response(
                    {"error": "User can join only one department"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        serializer = DepartmentMemberSerializer(department_member)
        return Response({"message": "Department member added successfully",
                        "added_member": serializer.data
                }, status=status.HTTP_201_CREATED)
    
class DepartmentEditMemberView(APIView):
    
    permission_classes = [IsAdminUser | IsChief]
    def patch(self, request, department_id, user_id):
        department_member = get_object_or_404(DepartmentMember, 
                                              user_id=user_id,
                                              department_id=department_id)
        serializer = DepartmentMemberSerializer(
            instance=department_member,
            data = request.data,
            partial=True
        )
        if serializer.is_valid():
                serializer.save()

                return Response({
                    "message": "Department member updated successfully",
                    "edited_member": serializer.data
                }, status=status.HTTP_200_OK)
        
    def delete(self, request, department_id, user_id):
        try:

            department_member = get_object_or_404(
                DepartmentMember, 
                user_id=user_id,
                department_id=department_id
            )
            serializer = DepartmentMemberSerializer(department_member)
            department_member.delete()
            
            return Response({
                "message": "Department member removed successfully",
                "deleted_member": serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

