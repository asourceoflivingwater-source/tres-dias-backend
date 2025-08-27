from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer
from django.shortcuts import get_object_or_404

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