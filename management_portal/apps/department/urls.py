from django.urls import path
from .views import DepartmentsListView, DepartmentProfileView

urlpatterns = [
    path('departments/', DepartmentsListView.as_view(), name='departments_view'),
    path('departments/<slug:slug>/', DepartmentProfileView.as_view(), name='department_profile_view'),

]