from django.urls import path
from .views import (
    DepartmentsListView,
    DepartmentProfileView,
    DepartmentSectionView,
    DepartmentMemberView,
    DepartmentMemberUpdateView,
)

urlpatterns = [
    path("departments/", DepartmentsListView.as_view(), name="departments_view"),
    path(
        "departments/<slug:slug>/",
        DepartmentProfileView.as_view(),
        name="department_profile_view",
    ),
    path(
        "departments/<slug:slug>/sections/",
        DepartmentSectionView.as_view(),
        name="department_sections_view",
    ),
    path(
        "departments/<uuid:department_id>/members/",
        DepartmentMemberView.as_view(),
        name="department-members-view",
    ),
    path(
        "departments/<uuid:department_id>/members/<uuid:user_id>",
        DepartmentMemberUpdateView.as_view(),
        name="department_edit_member_view",
    ),
]
