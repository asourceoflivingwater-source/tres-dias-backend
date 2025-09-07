from django.urls import path
from .views import SectionsEditView, SectionsPublishView

urlpatterns = [
    path('sections/<uuid:section_id>/', SectionsEditView.as_view(), name='section_edit_view'),
    path('sections/<uuid:section_id>/publish/', SectionsPublishView.as_view(), name='section_publish_view'),
]