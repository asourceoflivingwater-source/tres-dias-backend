from django.urls import path
from .views import (SectionsEditView, 
                    SectionsPublishView, 
                    SectionPermissionEditView,
                    MediaUploadView)

urlpatterns = [
    path('sections/<uuid:section_id>/', SectionsEditView.as_view(), name='section_edit_view'),
    path('sections/<uuid:section_id>/publish/', SectionsPublishView.as_view(), name='section_publish_view'),
    path('sections/<uuid:section_id>/permissions/' , SectionPermissionEditView.as_view(), name="section_permissions_edit_view"),
    path('media/', MediaUploadView.as_view(), name="media_upload_view")
]