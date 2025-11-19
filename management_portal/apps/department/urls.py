from django.urls import path
from .views import (DepartmentsListView, 
                    DepartmentProfileView,
                    DepartmentSectionsView,
                    DepartmentMemberView,
                    DepartmentMemberUpdateView)
from django.views.decorators.cache import cache_page
                    
urlpatterns = [
    path('departments/', DepartmentsListView.as_view(), name='departments_view'),
    path('departments/<slug:slug>/', DepartmentProfileView.as_view(), name='department_profile_view'),
    path('departments/<slug:slug>/sections/', cache_page(60*15)(DepartmentSectionsView.as_view()), name='department_sections_view'),
    path('departments/<uuid:department_id>/members/', DepartmentMemberView.as_view(), name="department-members-view"),
    path('departments/<uuid:department_id>/members/<uuid:user_id>', DepartmentMemberUpdateView.as_view(), name="department_edit_member_view")
    #path('sections/<uuid:department_id>')
]