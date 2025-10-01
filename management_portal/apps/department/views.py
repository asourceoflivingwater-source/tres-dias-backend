from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Department, DepartmentMember
from .serializers import DepartmentSerializer, DepartmentMemberSerializer
from apps.users.models import User
from apps.users.permissions import IsChief
from apps.sections.models import DepartmentSection
from apps.sections.serializers import DepartmentSectionSerializer
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

class DepartmentsListView(ListAPIView):
    permission_classes=[AllowAny]
    queryset = Department.objects.all()
    serializer_class= DepartmentSerializer

class DepartmentProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentMemberView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsChief]
    serializer_class= DepartmentMemberSerializer
    def get_queryset(self):
        return DepartmentMember.objects.filter(department_id=self.kwargs["department_id"])

    def create(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.get(email=data["user_email"])
        data['user'] = user.id
        data['department'] = self.kwargs["department_id"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class DepartmentMemberUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsChief]
    serializer_class = DepartmentMemberSerializer
    queryset = DepartmentMember.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
       
        obj = get_object_or_404(queryset, department_id=self.kwargs.get('department_id'),
                                user_id=self.kwargs.get('user_id'))
        self.check_object_permissions(self.request, obj)
        return obj
    
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
        
     


