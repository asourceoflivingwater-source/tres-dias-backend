from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.utils import IntegrityError
from apps.users.models import User
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from django.db.models import Q
from django.db.models import Q, F, Func, Value

class DepartmentsListView(APIView):

    def get(self, request):
        departments = get_list_or_404(Department)
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DepartmentProfileView(APIView):
    
    def get(self, request, slug):
        department = get_object_or_404(Department, slug=slug)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DepartmentSectionsView(APIView):

    permission_classes = [AllowAny] 

    def get(self, request, slug):
        qs = DepartmentSection.objects.filter(department__slug=slug)

        if not request.user.is_authenticated:
            qs = qs.filter(visibility="public", status="published")

        elif request.user.is_staff:
            pass

        elif getattr(request.user, "is_clergy", False) or getattr(request.user, "is_rectorate", False):
            qs = qs.filter(status="published")

        else:
            qs = qs.filter(
                        
                Q(visibility="public", status="published")
                | Q(
                    department__members__user=request.user,
                    department__members__is_active=True,
                    department__members__role="chief"
                )
                | Q(
                    department__members__user=request.user,
                    department__members__is_active=True,
                    department__members__role__in=F("visible_for_roles")
                )).distinct()
            
        serializer = DepartmentSectionSerializer(qs, many=True)
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

