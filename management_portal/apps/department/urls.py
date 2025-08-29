from django.urls import path
from .views import (DepartmentsListView, 
                    DepartmentProfileView,
                    DepartmentSectionsView,
                    DepartmentAddMemberView,
                    DepartmentEditMemberView)

urlpatterns = [
    path('departments/', DepartmentsListView.as_view(), name='departments_view'),
    path('departments/<slug:slug>/', DepartmentProfileView.as_view(), name='department_profile_view'),
    path('departments/<slug:slug>/sections/', DepartmentSectionsView.as_view(), name='department_sections_view'),
    path('departments/<uuid:id>/members/', DepartmentAddMemberView.as_view(), name="department_add_member_view"),
    path('departments/<uuid:department_id>/members/<uuid:user_id>', DepartmentEditMemberView.as_view(), name="department_edit_member_view")
    
]