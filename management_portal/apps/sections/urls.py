from django.urls import path
from .views import (SectionsView, 
                    SectionsPublishView, 
                    SectionPermissionEditView,
                    SectionVersionsView,
                    SectionVersionRevertView,
                    MediaUploadView)

urlpatterns = [
    path('sections/<uuid:section_id>/', SectionsView.as_view(), name='section_edit_view'),
    path('sections/<uuid:section_id>/publish/', SectionsPublishView.as_view(), name='section_publish_view'),
    path('sections/<uuid:section_id>/permissions/' , SectionPermissionEditView.as_view(), name="section_permissions_edit_view"),
    path('sections/<uuid:section_id>/versions/', SectionVersionsView.as_view(), name='section_versions_view'),
    path('sections/<uuid:section_id>/versions/<int:version>/revert/', SectionVersionRevertView.as_view(), name='version_revert_view'),
    path('media/', MediaUploadView.as_view(), name="media_upload_view")
]